import streamlit as st
import fitz  # PyMuPDF
import re
from datetime import datetime

def is_cover_page(page):
    text = page.get_text()
    return (
        "小池知事 定例記者会見" in text
        and "令和" in text
    )

def clean_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    pages_to_keep = []

    for i, page in enumerate(doc):
        if i in [0, 1]:
            continue
        if is_cover_page(page):
            continue
        pages_to_keep.append(i)

    new_doc = fitz.open()
    for i in pages_to_keep:
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    return new_doc

def extract_date_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = doc[0].get_text()
    match = re.search(r"令和(\d)年(\d+)月(\d+)日", text)
    if match:
        year = 2018 + int(match.group(1)) - 1
        month = int(match.group(2))
        day = int(match.group(3))
        return f"{year}.{month}.{day}"
    else:
        return datetime.today().strftime("%Y.%m.%d")

st.title("知事記者会見資料 PDF整形アプリ")

uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

if uploaded_file:
    date_str = extract_date_from_pdf(uploaded_file)
    uploaded_file.seek(0)  # 再度読み込む
    cleaned_pdf = clean_pdf(uploaded_file)

    output_filename = f"{date_str}知事記者会見.pdf"
    pdf_bytes = cleaned_pdf.tobytes()

    st.download_button(
        label="PDFをダウンロード",
        data=pdf_bytes,
        file_name=output_filename,
        mime="application/pdf"
    )
