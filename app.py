def process_pdf(file):
    from PyPDF2 import PdfReader, PdfWriter
    import pdfplumber
    import tempfile

    reader = PdfReader(file)
    writer = PdfWriter()

    # 表紙っぽい1ページ目は削除（仮）
    with pdfplumber.open(file) as pdf:
        first_page_text = pdf.pages[0].extract_text()
        date_str = extract_date(first_page_text)

    # 2ページ目以降をコピー（調整可能）
    for i in range(1, len(reader.pages)):
        writer.add_page(reader.pages[i])

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path, date_str
