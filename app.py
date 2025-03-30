import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import io
import re
from datetime import datetime

st.title("知事記者会見 PDF 整形ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def convert_wareki_to_seireki(text):
    match = re.search(r"(令和)(\d+)年(\d{1,2})月(\d{1,2})日", text)
    if match:
        year = 2018 + int(match.group(2))
        return f"{year}.{int(match.group(3))}.{int(match.group(4))}"
    return None

def extract_date(text, filename=None):
    match = re.search(r"(\d{4})[年./\- ]*(\d{1,2})[月./\- ]*(\d{1,2})日", text)
    if match:
        y, m, d = map(int, match.groups())
        return f"{y}.{m}.{d}"
    converted = convert_wareki_to_seireki(text)
    if converted:
        return converted
    if filename:
        match = re.search(r"(\d{1,2})月(\d{1,2})日", filename)
        if match:
            y = datetime.now().year
            m, d = map(int, match.groups())
            return f"{y}.{m}.{d}"
    return "日付未検出"

def is_centered_page(page, tolerance=0.2):
    width = page.width
    center_min = width * (0.5 - tolerance)
    center_max = width * (0.5 + tolerance)
    words = page.extract_words()
    if not words:
        return False
    centered_words = [w for w in words if center_min <= float(w['x0']) <= center_max]
    return len(centered_words) / len(words) > 0.7

def is_cover_like_page(page):
    text = page.extract_text() or ""
    has_title = "小池知事 定例記者会見" in text
    has_date = bool(
        re.search(r"\d{4}年\d{1,2}月\d{1,2}日", text) or
        re.search(r"令和\d+年\d{1,2}月\d{1,2}日", text)
    )
    return has_title and has_date and is_centered_page(page)

def process_pdf(file):
    file_bytes = file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    pages_to_delete = {0, 1}
    date_str = "日付未検出"

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if date_str == "日付未検出":
                date_str = extract_date(text, uploaded_file.name)
            if i > 1 and is_cover_like_page(page):
                pages_to_delete.add(i)

    for i in range(len(reader.pages)):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue(), date_str

if uploaded_file:
    with st.spinner("PDFを整形中..."):
        result_pdf, date_str = process_pdf(uploaded_file)
        filename = f"{date_str}知事記者会見資料.pdf"
        st.download_button(
            label=f"{filename} をダウンロード",
            data=result_pdf,
            file_name=filename,
            mime="application/pdf"
        )
