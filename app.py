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
    # ステップ1：表紙のテキスト
