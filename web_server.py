from flask import Flask, render_template, request
import urllib.parse
from main import scrape_kakaku_com, scrape_amazon, CATEGORY_URL_MAP, get_makers_for_category
import logging
import threading
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# --- カテゴリ定義 ---
PC_PARTS_CATEGORIES = [
    "CPU", "メモリ", "マザーボード", "グラフィックボード", 
    "SSD", "PCケース", "電源ユニット", "CPUクーラー"
]
ALL_CATEGORIES = list(CATEGORY_URL_MAP.keys())

# --- メーカーリストのキャッシュ ---
MAKER_LIST_CACHE = {}

# 周辺機器カテゴリを再定義
PERIPHERALS_CATEGORIES = [cat for cat in CATEGORY_URL_MAP.keys() if cat not in PC_PARTS_CATEGORIES]


def search_and_compare_for_maker(category_keyword, filter_keyword, limit, profit_margin, maker, sort):
    """指定された単一メーカーの製品を検索・比較する"""
    logging.info(f"  -> メーカー '{maker}' の検索処理を開始...")
    kakaku_results, _ = scrape_kakaku_com(category_name=category_keyword, filter_keyword=filter_keyword, limit=limit, maker=maker, sort=sort)
    
    if not kakaku_results:
        logging.info(f"  -> メーカー '{maker}' の製品は見つかりませんでした。")
        return []

    maker_results = []
    for item in kakaku_results:
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
    results = []
    category_name = ''
    filter_keyword = ''
    limit = 3
    profit_margin = 15
    selected_makers = []
    selected_sort = 'price_asc'
    
    if request.method == 'POST':
        category_name = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        limit = int(request.form.get('limit', 3))
        profit_margin = int(request.form.get('profit_margin', 15))
        selected_makers = request.form.getlist('makers')
        selected_sort = request.form.get('sort', 'price_asc')
        
        if category_name and selected_makers:
            logging.info(f"検索リクエスト受信: カテゴリ='{category_name}', メーカー='{selected_makers}', 1メーカーあたりの上限='{limit}'")
            all_results = []
            for maker in selected_makers:
                maker_results = search_and_compare_for_maker(category_name, filter_keyword, limit, profit_margin, maker, selected_sort)
                all_results.extend(maker_results)
            results = sorted(all_results, key=lambda x: x.get('profit_margin', 0), reverse=True)
    
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
        peripherals_categories=PERIPHERALS_CATEGORIES, # 変更
        makers_by_category_json=makers_by_category_json
    )

if __name__ == '__main__':
    # アプリケーション起動時に一度だけメーカーリストを読み込む
    preload_thread = threading.Thread(target=preload_maker_lists)
    preload_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
