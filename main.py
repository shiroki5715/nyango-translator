# このファイルはアプリケーションのエントリポイントとして機能しますが、
# 主要なロジックは他のモジュールに分割されています。
#
# web_server.py: Flaskアプリケーションのルーティングとサーバー起動
# search.py:     検索とデータ比較のコアロジック (今後作成予定)
# scrapers/:     各ウェブサイトからのデータ取得ロジック
# config.py:     アプリケーション全体の設定
# utils.py:      共通のユーティリティ関数

import logging

# アプリケーションの主要な処理は web_server.py から開始されます。
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')
    logging.info("アプリケーションを起動するには web_server.py を実行してください。")