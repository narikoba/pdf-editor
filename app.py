import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import io
import re
from datetime import datetime

st.title("知事記者会見 PDF 整形ツール（表紙・構成類似ページ自動削除）")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def extract_date(text, filename=None):
    match = re.search(r"(\d{4})[年.\s]*([0-9]{1,2})[月.\s]*([0-9]{1,2})日", text)
    if match:
        year, month, day = map(int, match.groups())
        return f"{year}.{month}.{day}"
    if filename:
        match = re.search(r"(\d{1,2})月(\d{1,2})日", filename)
        if match:
            month, day = map(int, match.groups())
            year = datetime.now().year
            return f"{year}.{month}.{day}"
    return "日付未検出"

def is_centered_page(page, tolerance=0.2):
    width = page.width
    center_min = width * (0.5 - tolerance)
    center_max = width * (0.5 + tolerance)

    words = page.extract_words()
    if not words:
        return False

    centered_words = [w for w in words if center_min <= float(w['x0']) <= center_max]
    ratio = len(centered_words) / len(words)
    return ratio > 0.7  # 70%以上が中央寄せならTrue

def is_cover_like(text):
    return (
        "小池知事 定例記者会見" in text and
        re.search(r"\d{4}年\d{1,2}月\d{1,2}日", text)
    )

def page_structure_summary(page):
    words = page.extract_words()
    if not words:
        return (0, 0)
    avg_x = sum(float(w["x0"]) for w in words) / len(words)
    return len(words), avg_x

def is_similar_to_page(page, reference_len, reference_avg_x, tolerance_len=5, tolerance_x=30):
    length, avg_x = page_structure_summary(page)
    return abs(length - reference_len) <= tolerance_len and abs(avg_x - reference_avg_x) <= tolerance_x

def process_pdf(file):
    file_bytes = file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()

    date_str = "日付未検出"
    pages_to_delete = set([0, 1])  # 1ページ目と2ページ目は無条件削除

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        if len(pdf.pages) > 1:
            ref_len, ref_avg_x = page_structure_summary(pdf.pages[1])
        else:
            ref_len, ref_avg_x = 0, 0

        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if date_str == "日付未検出":
                date_str = extract_date(text, uploaded_file.name)

            if i <= 1:
                continue  # 最初の2ページは削除済み
            if is_cover_like(text) and is_centered_page(page) and is_similar_to_page(page, ref_len, ref_avg_x):
                pages_to_delete.add(i)

    for i in range(len(reader.pages)):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue(), date_str

if uploaded_file:
    with st.spinner("PDFを処理中..."):
        result_pdf, date_str = process_pdf(uploaded_file)
        filename = f"{date_str}知事記者会見.pdf"
        st.download_button(
            label=f"{filename} をダウンロード",
            data=result_pdf,
            file_name=filename,
            mime="application/pdf"
        )
