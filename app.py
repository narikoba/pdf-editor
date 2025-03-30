import streamlit as st
import os
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from japanera import Japanera
import tempfile

st.title("知事記者会見資料 PDF 整形ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def extract_date(text):
    import re
    match = re.search(r"令和(\d)年(\d{1,2})月(\d{1,2})日", text)
    if match:
        era_year, month, day = map(int, match.groups())
        western_year = 2018 + era_year
        return f"{western_year}.{month}.{day}"
    return None

def is_cover_page(text):
    return "小池知事 定例記者会見" in text and "令和" in text

def process_pdf(file):
    cover_pages = []
    extracted_date = None

    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if i == 0:
                cover_pages.append(i)
            elif is_cover_page(text):
                cover_pages.append(i)
                if not extracted_date:
                    extracted_date = extract_date(text)

    if not extracted_date:
        extracted_date = "未検出"

    reader = PdfReader(file)
    writer = PdfWriter()
    for i in range(len(reader.pages)):
        if i not in cover_pages:
            writer.add_page(reader.pages[i])

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path, extracted_date

if uploaded_file:
    with st.spinner("PDFを処理中..."):
        output_file, date_str = process_pdf(uploaded_file)
        filename = f"{date_str}知事記者会見資料.pdf"
        with open(output_file, "rb") as f:
            st.download_button(
                label=f"{filename} をダウンロード",
                data=f.read(),
                file_name=filename,
                mime="application/pdf"
            )
