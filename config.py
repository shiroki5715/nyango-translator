# アプリケーション設定ファイル

import os

# --- Flask設定 ---
# 本番環境では環境変数から取得することを推奨
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_very_secret_key_for_development')

# --- カテゴリ定義 ---
PC_PARTS_CATEGORIES = [
    "CPU", "メモリ", "マザーボード", "グラフィックボード", "SSD", 
    "ハードディスク・HDD(3.5インチ)", "ハードディスク・HDD(2.5インチ)", "ハードディスク・HDD(SCSI)",
    "PCケース", "電源ユニット", "CPUクーラー", "サウンドカード", "ケースファン", 
    "キャプチャーボード", "DVDドライブ", "ブルーレイドライブ"
]

PERIPHERALS_CATEGORIES = [
    "PCモニター・液晶ディスプレイ", "VRゴーグル・VRヘッドセット", "モニターアーム",
    "プリンタ", "スキャナ", "マウス", "キーボード", "テンキー", "WEBカメラ",
    "NAS(ネットワークHDD)", "無線LANルーター(Wi-Fiルーター)"
]

# メーカーリストを事前取得する対象カテゴリ
PRELOAD_CATEGORIES = PC_PARTS_CATEGORIES + PERIPHERALS_CATEGORIES

# --- 価格.com URLマップ ---
CATEGORY_URL_MAP = {
    # PCパーツ
    "CPU": "https://kakaku.com/specsearch/0510/",
    "CPUクーラー": "https://kakaku.com/specsearch/0512/",
    "メモリ": "https://kakaku.com/specsearch/0520/",
    "マザーボード": "https://kakaku.com/specsearch/0540/",
    "グラフィックボード": "https://kakaku.com/specsearch/0550/",
    "SSD": "https://kakaku.com/specsearch/0537/",
    "ハードディスク・HDD(3.5インチ)": "https://kakaku.com/specsearch/0530/",
    "ハードディスク・HDD(2.5インチ)": "https://kakaku.com/specsearch/0535/",
    "ハードディスク・HDD(SCSI)": "https://kakaku.com/specsearch/0536/",
    "PCケース": "https://kakaku.com/specsearch/0580/",
    "電源ユニット": "https://kakaku.com/specsearch/0590/",
    "サウンドカード": "https://kakaku.com/specsearch/0560/",
    "ケースファン": "https://kakaku.com/specsearch/0581/",
    "キャプチャーボード": "https://kakaku.com/specsearch/0568/",
    "DVDドライブ": "https://kakaku.com/specsearch/0125/",
    "ブルーレイドライブ": "https://kakaku.com/specsearch/0126/",
    # 周辺機器
    "PCモニター・液晶ディスプレイ": "https://kakaku.com/specsearch/0085/",
    "VRゴーグル・VRヘッドセット": "https://kakaku.com/specsearch/0576/",
    "モニターアーム": "https://kakaku.com/specsearch/0086/",
    "プリンタ": "https://kakaku.com/specsearch/0060/",
    "スキャナ": "https://kakaku.com/specsearch/0070/",
    "マウス": "https://kakaku.com/specsearch/0160/",
    "キーボード": "https://kakaku.com/specsearch/0150/",
    "テンキー": "https://kakaku.com/specsearch/0153/",
    "WEBカメラ": "https://kakaku.com/specsearch/0567/",
    "NAS(ネットワークHDD)": "https://kakaku.com/specsearch/0538/",
    "無線LANルーター(Wi-Fiルーター)": "https://kakaku.com/specsearch/0077/",
}

# --- ファイルパス設定 ---
EXCLUDED_MAKERS_FILE = 'exclude_makers.txt'
EXCLUDED_KEYWORDS_FILE = 'exclude_keywords.txt'
