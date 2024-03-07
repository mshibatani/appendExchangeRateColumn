# appendExchangeRateColumn

# CSVファイルに為替レートカラム挿入

## 概要
* CSVファイルを入力し、為替レートを追加しファイル出力します。
* 日付カラムを含むCSVファイルを選択。TTS/TTM/TTBのいずれかを選択して実行。
* 出力ファイル名 "_out.csv" を追加します。
* 日時カラムを判別するのに使われるタイトル文字列はソースリストにハードコードされておりカスタマイズ可能。
* 為替レートのソースに三菱UFJ銀行の公開データを使用。(一度使用した日付の為替レートはキャッシュされる)

## Summary
* Identifies the date column in a CSV file
* You can customize the strings that indicate date column.
* Retrieves the exchange rate for that day from Mitsubishi UFJ Bank's data available on the internet
* Adds a new column to the CSV file based on the retrieved exchange rate

## System Requirements: 動作環境
* macOS

## Required modules: 使用モジュール
* pandas
* chardet
* percache
* PySimpleGUI
