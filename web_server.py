from flask import Flask, render_template, request, jsonify
import urllib.parse
from main import scrape_kakaku_com, scrape_amazon, CATEGORY_URL_MAP
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

MAKER_CACHE = {}
PC_PARTS_CATEGORIES = [cat for cat, url in CATEGORY_URL_MAP.items() if "pc" in url or "05" in url.split('/')[-2] or "01" in url.split('/')[-2]]
PERIPHERALS_CATEGORIES = [cat for cat in CATEGORY_URL_MAP.keys() if cat not in PC_PARTS_CATEGORIES]


def cache_all_makers():
    logging.info("--- 全カテゴリのメーカーリストのキャッシュを開始します ---")
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_category = {executor.submit(scrape_kakaku_com, category, get_makers_only=True): category for category in CATEGORY_URL_MAP.keys()}
        for future in future_to_category:
            category = future_to_category[future]
            try:
                makers = future.result()
                MAKER_CACHE[category] = makers
            except Exception as exc:
                logging.error(f"'{category}' のメーカー取得中にエラーが発生しました: {exc}")
    logging.info("--- 全てのメーカーリストのキャッシュが完了しました ---")

def search_and_compare(category_keyword, filter_keyword, limit, profit_margin, maker=None, sort=None):
    logging.info(f"検索処理を開始: カテゴリ='{category_keyword}', メーカー='{maker}', ソート='{sort}'")
    kakaku_results, _ = scrape_kakaku_com(category_name=category_keyword, filter_keyword=filter_keyword, limit=limit, maker=maker, sort=sort)
    
    if not kakaku_results:
        return []

    final_results = []
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = [executor.submit(scrape_amazon, item['name']) for item in kakaku_results]
        for i, future in enumerate(futures):
            item = kakaku_results[i]
            amazon_result = future.result()
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
                    final_results.append(item)
    return final_results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    category_name = ''
    filter_keyword = ''
    limit = 5
    profit_margin = 15
    selected_maker = ''
    selected_sort = 'price_asc'
    
    if request.method == 'POST':
        category_name = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        limit = int(request.form.get('limit', 5))
        profit_margin = int(request.form.get('profit_margin', 15))
        selected_maker = request.form.get('maker', '')
        selected_sort = request.form.get('sort', 'price_asc')
        if category_name:
            results = search_and_compare(category_name, filter_keyword, limit, profit_margin, selected_maker, selected_sort)
    
    return render_template(
        'index.html', 
        results=results, 
        category_name=category_name, 
        filter_keyword=filter_keyword,
        limit=limit,
        profit_margin=profit_margin,
        makers=MAKER_CACHE.get(category_name, []),
        selected_maker=selected_maker,
        selected_sort=selected_sort,
        pc_parts_categories=PC_PARTS_CATEGORIES,
        peripherals_categories=PERIPHERALS_CATEGORIES
    )

@app.route('/get_makers_for_category')
def get_makers_for_category():
    category = request.args.get('category', '')
    return jsonify(MAKER_CACHE.get(category, []))

if __name__ == '__main__':
    caching_thread = threading.Thread(target=cache_all_makers, name="MakerCacheThread")
    caching_thread.daemon = True
    caching_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
