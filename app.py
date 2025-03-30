import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import tempfile
from fpdf import FPDF
from pdf2image import convert_from_bytes
import os
import io

st.title("知事記者会見 PDF 整形＋軽量化ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")
light_mode = st.checkbox("ガラケー向けに軽量化する（画像ベース）")

def extract_date(text):
    import re
    match = re.search(r"(\d{4})[年.\s]*(\d{1,2})[月.\s]*(\d{1,2})日", text)
    if match:
        year, month, day = map(int, match.groups())
        return f"{year}.{month}.{day}"
    return "日付未検出"

def standard_process(file):
    cover_pages = [0]
    date_str = "日付未検出"
    with pdfplumber.open(file) as pdf:
        first_page_text = pdf.pages[0].extract_text() or ""
        date_str = extract_date(first_page_text)

    reader = PdfReader(file)
    writer = PdfWriter()
    for i in range(len(reader.pages)):
        if i not in cover_pages:
            writer.add_page(reader.pages[i])

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(temp_path, "wb") as f:
        writer.write(f)
    return temp_path, date_str

def light_process(file, date_str):
    images = convert_from_bytes(file.read(), dpi=100, first_page=2)  # skip 1st page
    pdf = FPDF(unit="mm", format="A4")
    for img in images:
        pdf.add_page()
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp_img.name, "JPEG")
        pdf.image(temp_img.name, x=0, y=0, w=210, h=297)
        os.unlink(temp_img.name)

    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()

if uploaded_file:
    with st.spinner("PDFを処理中..."):
        temp_pdf_path, date_str = standard_process(uploaded_file)

        if light_mode:
            with open(temp_pdf_path, "rb") as f:
                result_pdf = light_process(f, date_str)
            filename = f"{date_str}知事記者会見_軽量版.pdf"
            st.download_button(
                label=f"{filename} をダウンロード",
                data=result_pdf,
                file_name=filename,
                mime="application/pdf"
            )
        else:
            with open(temp_pdf_path, "rb") as f:
                result_pdf = f.read()
            filename = f"{date_str}知事記者会見.pdf"
            st.download_button(
                label=f"{filename} をダウンロード",
                data=result_pdf,
                file_name=filename,
                mime="application/pdf"
            )
