import streamlit as st
from PyPDF2 import PdfReader
import pdfplumber
import tempfile
from fpdf import FPDF
from pdf2image import convert_from_bytes
import os
import io

st.title("知事記者会見 PDF 整形ツール（軽量化自動処理）")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def extract_date(text):
    import re
    match = re.search(r"(\d{4})[年.\s]*(\d{1,2})[月.\s]*(\d{1,2})日", text)
    if match:
        year, month, day = map(int, match.groups())
        return f"{year}.{month}.{day}"
    return "日付未検出"

def process_light_pdf(file):
    # ステップ1：表紙のテキストから日付を抽出
    with pdfplumber.open(file) as pdf:
        first_page_text = pdf.pages[0].extract_text() or ""
        date_str = extract_date(first_page_text)

    # ステップ2：画像ベースPDFとして出力（2ページ目以降のみ）
    images = convert_from_bytes(file.read(), dpi=100, first_page=2)
    pdf = FPDF(unit="mm", format="A4")
    for img in images:
        pdf.add_page()
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp_img.name, "JPEG")
        pdf.image(temp_img.name, x=0, y=0, w=210, h=297)
        os.unlink(temp_img.name)

    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue(), date_str

if uploaded_file:
    with st.spinner("PDFを軽量化＆整形中..."):
        result_pdf, date_str = process_light_pdf(uploaded_file)
        filename = f"{date_str}知事記者会見.pdf"
        st.download_button(
            label=f"{filename} をダウンロード",
            data=result_pdf,
            file_name=filename,
            mime="application/pdf"
        )
        
