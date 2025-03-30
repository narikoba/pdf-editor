import streamlit as st
import fitz  # PyMuPDF
import io
import tempfile
from fpdf import FPDF
import pdfplumber
import os
import re
from datetime import datetime

st.title("知事記者会見 PDF 整形ツール（軽量化自動処理）")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

def extract_date(text, filename=None):
    # 優先1：本文から日付を抽出（例：2025年3月28日）
    match = re.search(r"(\d{4})[年.\s]*(\d{1,2})[月.\s]*(\d{1,2})日", text)
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

def process_light_pdf(file):
    file_bytes = file.read()

    # 日付取得（本文 + ファイル名）
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        first_page_text = pdf.pages[0].extract_text() or ""
        date_str = extract_date(first_page_text, uploaded_file.name)

    # 画像化（2ページ目以降）
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pdf = FPDF(unit="mm", format="A4")
    zoom =
