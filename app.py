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
    center_max = width * (0.5 +*_
