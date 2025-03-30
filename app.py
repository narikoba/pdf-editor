import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import tempfile
import io
import re
from datetime import datetime

st.title("知事記者会見 PDF 整形ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def extract_date(text, filename=None):
    # 優先1：本文から抽出（西暦表記）
    match = re.search(r"(\d{4})[年.\s]*([0-9]{1,2})[月.\s]*([0-9]{1,2})日", text)
    if match:
        year, month, day = map(int, match.groups())
        return f"{year}.{month}.{day}"

    # 優先2：ファイル名から抽出（例：1月17日）
    if filename:
        match = re.search(r"(\d{1,2})月(\d{1,2})日", filename)
        if match:
            month, day = map(int, match.groups())
            current_year = datetime.now().year
            return f"{current_year}.{month}.{day}"

    return "日付未検出"

def is_cover_like(text):
    """表紙的ページを検出：「小池知事 定例記者会見」と日付が含まれる"""
    if not text:
        return False
    if "小池知事 定例記者会見" in text and re.search(r"\d{4}年\d{1,2}月\d{1,2}日", text):
        return True
    return False

def process_pdf(file):
    file_bytes = file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()

    # 表紙ページ候補の番号を特定
    cover_pages = set()
    date_str = "日付未検出"

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if i == 0:
                cover_pages.add(i)
            elif is_cover_like(text):
                cover_pages.add(i)
            if date_str == "日付未検出":
                date_str = extract_date(text, uploaded_file.name)

    # 残すページを追加
    for i in range(len(reader.pages)):
        if i not in cover_pages:
            writer.add_page(reader.pages[i])

    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    return output_pdf.getvalue(), date_str

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
