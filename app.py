import pdfplumber
import os
from PyPDF2 import PdfReader, PdfWriter
from japanera import Japanera

def extract_date(text):
    import re
    # 和暦日付を探す
    match = re.search(r"令和(\d)年(\d{1,2})月(\d{1,2})日", text)
    if match:
        era_year, month, day = map(int, match.groups())
        western_year = 2018 + era_year  # 令和元年＝2019年
        return f"{western_year}.{month}.{day}"
    return None

def is_cover_page(text):
    return "小池知事 定例記者会見" in text and "令和" in text

def process_pdf(input_path):
    # 1. テキストを使って表紙ページを特定
    cover_pages = []
    extracted_date = None

    with pdfplumber.open(input_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if i == 0:
                cover_pages.append(i)  # 最初のページは必ず削除
            elif is_cover_page(text):
                cover_pages.append(i)
                if not extracted_date:
                    extracted_date = extract_date(text)

    if not extracted_date:
        print("日付が見つかりませんでした。処理を中止します。")
        return

    # 2. 新しいPDFを作成（必要なページだけを追加）
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        if i not in cover_pages:
            writer.add_page(reader.pages[i])

    # 3. ファイル名の自動生成
    output_filename = f"{extracted_date}知事記者会見資料.pdf"
    output_path = os.path.join(os.path.dirname(input_path), output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"保存完了: {output_path}")

# 実行（ファイルパスを書き換えてください）
process_pdf("3月28日 小池知事定例記者会見資料.pdf")
