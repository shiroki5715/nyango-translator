# Gemini Handoff - PCパーツ価格差・自動分析ツール

## 最終更新日時
2025年7月27日

## 1. プロジェクトの最終目標（どんなツールを作るのか？）
AmazonでのPCパーツせどりを効率化するため、複数ECサイトとAmazonの価格差を自動で分析する**ローカルWebアプリケーション**を開発する。ユーザーはブラウザからツールを操作し、仕入れ先サイトのURLと利益率（%）を指定するだけで、利益の出る商品をリストとして受け取れることを目指す。

## 2. コア機能と技術仕様
- **UI:** Python FlaskによるWebサーバーをローカルで起動し、ブラウザで操作画面を提供する。
- **情報収集:** Python Playwrightを使い、ブラウザを自動操作して、各ECサイトから商品情報を正確に取得する。
- **商品マッチング（ハイブリッド方式）:**
  1.  **ルールベース一次判定:** 正規化した型番の文字列比較で、高速・無料で大部分のマッチングを行う。
  2.  **AI二次判定:** 判断が難しい候補のみ、**Gemini API**に問い合わせて高精度な最終判断を仰ぐ。
  3.  **学習ノート機能:** AIの判断結果をローカルに記録・蓄積し、使えば使うほど高速化・低コスト化する自己改善機能を持たせる。

## 3. 仕入れ先候補サイトリスト（全18サイト）
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

## 4. これまでの進捗
- **[完了]** 開発環境の構築、Gitリポジトリの設定。
- **[完了]** FlaskによるUIプロトタイプの表示。
- **[完了]** `main.py`にTSUKUMOのスクレイピング機能（v1）を実装。

## 5. 現在の課題（ここで中断）
- `main.py`のテスト実行に失敗。原因は、プログラムに記述した**CSSセレクタが、実際のTSUKUMOのサイト構造と一致していない**ため。

## 6.【重要】次回、開始するタスク（ここから再開）
**目的:** Playwrightの`codegen`機能を使い、TSUKUMOの商品情報を指し示す**「正しいCSSセレクタ」**を特定する。

### 【あなたの次のアクション】
1.  黒い画面（コマンドプロンプト）で、以下のコマンドを実行してください。
    ```
    playwright codegen https://shop.tsukumo.co.jp/search/c:101010/
    ```
2.  表示されたブラウザウィンドウで、**いずれか1つの商品の「商品名」にマウスカーソルを合わせてください。**
3.  もう一方の「Playwright Inspector」ウィンドウに自動で入力されるコード（`page.get_by_...`で始まる行）をコピーし、私に教えてください。

### 【私の次のアクション】
1.  あなたが教えてくれたコードから、正しいCSSセレクタを抽出します。
2.  そのセレクタを使って`main.py`を修正し、TSUKUMOからの情報取得を成功させます。