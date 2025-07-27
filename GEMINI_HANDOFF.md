# Gemini Handoff

## 最終更新日時
2025年7月27日

## プロジェクトの現状サマリー

### 方針
当初のChrome拡張機能開発は、技術的制約により中断。Amazonの商品リストを基準とし、ユーザーが指定した複数のECサイトの商品を自動で巡回・価格比較する、**ローカルWebアプリケーション**の開発に方針を転換した。

### 現在の進捗
- **環境構築完了:** Python、Playwright、Flaskのインストールが完了し、開発環境が整った。
- **プロトタイプ完成:** FlaskによるWebサーバーを構築し、ブラウザ（`http://127.0.0.1:5000`）で基本的な操作画面（URL入力欄、価格差入力欄、実行ボタン）を表示できるようになった。

### 仕入れ先候補サイトリスト（攻略フェーズ案）
**フェーズ1：PC専門店（王道）**
- https://shop.tsukumo.co.jp/
- https://www.dospara.co.jp/
- https://www.pc-koubou.jp/

**フェーズ2：PC専門店（準大手・専門）**
- https://www.ark-pc.co.jp/
- https://www.pc4u.co.jp/
- https://www.1-s.jp/
- https://www.sofmap.com/
- https://www.oliospec.com/

**フェーズ3：大手量販店・総合通販**
- https://www.yodobashi.com/
- https://www.biccamera.com/bc/main/
- https://www.kojima.net/ec/index.html
- https://joshinweb.jp/top.html
- https://www.xprice.co.jp/

**フェーズ4：モール型ECサイト（最難関）**
- https://shopping.yahoo.co.jp/
- https://www.rakuten.co.jp/

**その他（要調査）**
- https://www.at-mac.com/
- https://www1.pcdepot.co.jp/
- https://shop.applied-net.co.jp/

### 次のステップ
- Webアプリの「分析を開始」ボタンを押した際の、バックエンド処理（`main.py`）の実装。
- `main.py`に、Playwrightを使ったWebスクレイピング機能と、型番マッチングロジックを組み込む。
