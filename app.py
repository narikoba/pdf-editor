import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
import io
import re
import fitz  # PyMuPDF
from datetime import datetime
from PIL import Image

st.title("知事記者会見 PDF 整形ツール（削除ページプレビュー付き）")

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

def render_page_image(pdf_bytes, page_number):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_number)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def process_pdf(file, preview=False):
    file_bytes = file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()
    pages_to_delete = {0, 1}
    delete_reasons = {}
    date_str = "日付未検出"

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if date_str == "日付未検出":
                date_str = extract_date(text, uploaded_file.name)
            if i == 0:
                delete_reasons[i] = "1ページ目（自動削除）"
            elif i == 1:
                delete_reasons[i] = "2ページ目（自動削除）"
            elif is_cover_like_page(page):
                pages_to_delete.add(i)
                delete_reasons[i] = "表紙的ページ（中央寄せ＋タイトル＋日付）"

    if preview:
        st.subheader("🔍 削除予定ページプレビュー")
        for i in sorted(pages_to_delete):
            st.markdown(f"**ページ {i + 1}：{delete_reasons.get(i)}**")
            image = render_page_image(file_bytes, i)
            st.image(image, width=400)

    for i in range(len(reader.pages)):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue(), date_str

if uploaded_file:
    show_preview = st.checkbox("削除予定ページを確認する（プレビュー表示）", value=True)
    with st.spinner("PDFを処理中..."):
        result_pdf, date_str = process_pdf(uploaded_file, preview=show_preview)
        filename = f"{date_str}知事記者会見資料.pdf"
        st.download_button(
            label=f"{filename} をダウンロード",
            data=result_pdf,
            file_name=filename,
            mime="application/pdf"
        )
