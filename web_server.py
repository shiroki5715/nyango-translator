from flask import Flask, render_template, request, session, redirect, url_for
import urllib.parse
from main import scrape_kakaku_com, scrape_amazon, CATEGORY_URL_MAP, get_makers_for_category
import logging
import threading
import json
import re
import concurrent.futures


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your_very_secret_key_for_development'  # セッション管理のための秘密鍵

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

# --- メーカーリストのキャッシュ ---
MAKER_LIST_CACHE = {}

def preload_maker_lists():
    """主要カテゴリのメーカーリストをバックグラウンドで事前に読み込む"""
    logging.info("メーカーリストの事前読み込みを開始...")
    for category in PRELOAD_CATEGORIES:
        if category not in MAKER_LIST_CACHE:
            makers = get_makers_for_category(category)
            if makers:
                MAKER_LIST_CACHE[category] = makers
    logging.info("メーカーリストの事前読み込みが完了。")



def search_and_compare_for_maker(category_keyword, filter_keyword, limit, profit_margin, maker, sort):
    """指定された単一メーカーの製品を検索・比較する"""
    logging.info(f"  -> メーカー '{maker}' の検索処理を開始...")
    kakaku_results, _ = scrape_kakaku_com(category_name=category_keyword, filter_keyword=filter_keyword, limit=limit, maker=maker, sort=sort)
    
    if not kakaku_results:
        logging.info(f"  -> メーカー '{maker}' の製品は見つかりませんでした。")
        return []

    # --- 重複排除ロジック ---
    logging.info(f"  -> 取得した {len(kakaku_results)} 件の製品から重複を排除します...")
    unique_products = {}
    for item in kakaku_results:
        # 製品名からメーカー名 [〇〇] や【〇〇】を削除
        base_name = re.sub(r'[\[【].*?[\]】]', '', item['name']).strip()
        # 製品名をスペースで分割し、最初の3要素をキーとする（製品シリーズを特定するため）
        product_key = ' '.join(base_name.split()[:3])

        # 辞書にキーが存在しないか、存在しても現在の価格の方が安い場合は登録/更新
        if product_key not in unique_products or item['price'] < unique_products[product_key]['price']:
            unique_products[product_key] = item
    
    # 重複排除後のリスト
    deduplicated_results = list(unique_products.values())
    logging.info(f"  -> 重複排除後、{len(deduplicated_results)} 件の製品が残りました。")
    # --- 重複排除ロジックここまで ---

    maker_results = []
    for item in deduplicated_results:
        amazon_result = scrape_amazon(item['name'])
        if amazon_result:
            item['amazon_price'] = amazon_result.get('price')
            item['amazon_url'] = amazon_result.get('url')
        else:
            item['amazon_price'] = None
            item['amazon_url'] = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(item['name'])}"
        
        if item.get('amazon_price') and item.get('price') and item.get('price') > 0:
            profit = item['amazon_price'] - item['price']
            margin = (profit / item['price']) * 100
            item['price_difference'] = profit
            item['profit_margin'] = margin
            if margin >= profit_margin:
                maker_results.append(item)
    
    logging.info(f"  -> メーカー '{maker}' の処理完了。{len(maker_results)}件の利益商品を発見。")
    return maker_results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームデータをセッションに保存
        session['form_data'] = request.form
        
        # 検索処理
        category_name = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        limit = int(request.form.get('limit', 3))
        profit_margin = int(request.form.get('profit_margin', 15))
        selected_makers = request.form.getlist('makers')
        selected_sort = request.form.get('sort', 'price_asc')
        
        results = []
        if category_name and selected_makers:
            logging.info(f"検索リクエスト受信: カテゴリ='{category_name}', メーカー='{selected_makers}', 1メーカーあたりの上限='{limit}'")
            all_results = []
            # --- 並列処理による高速化 ---
            # 同時に実行する最大スレッド数を5に制限
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # 各メーカーに対する検索タスクを作成
                future_to_maker = {
                    executor.submit(search_and_compare_for_maker, category_name, filter_keyword, limit, profit_margin, maker, selected_sort): maker 
                    for maker in selected_makers
                }
                # 完了したタスクから結果を取得
                for future in concurrent.futures.as_completed(future_to_maker):
                    maker = future_to_maker[future]
                    try:
                        maker_results = future.result()
                        all_results.extend(maker_results)
                    except Exception as exc:
                        logging.error(f"メーカー '{maker}' の処理中にエラーが発生しました: {exc}")
            
            results = sorted(all_results, key=lambda x: x.get('profit_margin', 0), reverse=True)
        
        # 検索結果をセッションに保存
        session['results'] = results
        
        # PRGパターン: POST後にリダイレクト
        return redirect(url_for('index'))

    # GETリクエストの処理
    # セッションからデータを取得（なければデフォルト値）
    form_data = session.pop('form_data', {})
    results = session.pop('results', [])
    
    # テンプレートに渡す変数を設定
    category_name = form_data.get('category_keyword', '')
    filter_keyword = form_data.get('filter_keyword', '')
    limit = int(form_data.get('limit', 3))
    profit_margin = int(form_data.get('profit_margin', 15))
    # getlistに相当する処理
    selected_makers = form_data.getlist('makers') if hasattr(form_data, 'getlist') else form_data.get('makers', [])
    selected_sort = form_data.get('sort', 'price_asc')

    makers_by_category_json = json.dumps(MAKER_LIST_CACHE)

    return render_template(
        'index.html', 
        results=results, 
        category_name=category_name, 
        filter_keyword=filter_keyword,
        limit=limit,
        profit_margin=profit_margin,
        selected_makers=selected_makers,
        selected_sort=selected_sort,
        pc_parts_categories=PC_PARTS_CATEGORIES,
        peripherals_categories=PERIPHERALS_CATEGORIES,
        makers_by_category_json=makers_by_category_json
    )

if __name__ == '__main__':
    # アプリケーション起動時に一度だけメーカーリストを読み込む
    preload_thread = threading.Thread(target=preload_maker_lists)
    preload_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
