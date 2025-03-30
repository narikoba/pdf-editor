# 知事記者会見 PDF整形アプリ

毎週金曜に配信される「小池知事 定例記者会見」PDF資料を整形するための Streamlit アプリです。

## 🔧 機能

- アップロードされたPDFのうち、以下のページを自動で削除します：
  - 1ページ目（表紙）
  - 2ページ目（次第など）
  - その他「表紙的なページ」（例：「小池知事 定例記者会見」＋「令和○年○月○日」を含むページ）

- 整形されたPDFのファイル名を、日付ベースで自動命名（例：`2025.3.28知事記者会見.pdf`）

## 🚀 使用方法

1. このリポジトリをクローンします

```bash
git clone https://github.com/your-username/governor-pdf-cleaner.git
cd governor-pdf-cleaner
