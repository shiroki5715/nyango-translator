from flask import Flask, render_template, request, session, redirect, url_for
import logging
import threading
import json
import config
import search
from scrapers import kakaku

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s')

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = config.SECRET_KEY

# --- メーカーリストのキャッシュ ---
MAKER_LIST_CACHE = {}

def preload_maker_lists():
    """主要カテゴリのメーカーリストをバックグラウンドで事前に読み込む"""
    logging.info("メーカーリストの事前読み込みを開始...")
    for category in config.PRELOAD_CATEGORIES:
        if category not in MAKER_LIST_CACHE:
            # 正しい関数を呼び出すように修正
            makers = kakaku.get_makers(category)
            if makers:
                MAKER_LIST_CACHE[category] = makers
    logging.info("メーカーリストの事前読み込みが完了。")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # フォームデータをセッションに保存
        session['form_data'] = request.form
        
        # searchモジュールに関数を移譲
        category_name = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        limit = int(request.form.get('limit', 10))
        profit_margin = int(request.form.get('profit_margin', 15))
        selected_makers = request.form.getlist('makers')
        selected_sort = request.form.get('sort', 'price_asc')
        
        results = []
        if category_name and selected_makers:
            results = search.run_search(
                category_name, 
                filter_keyword, 
                limit, 
                profit_margin, 
                selected_makers, 
                selected_sort
            )
        
        # 検索結果をセッションに保存
        session['results'] = results
        
        # PRGパターン: POST後にリダイレクト
        return redirect(url_for('index'))

    # GETリクエストの処理
    form_data = session.pop('form_data', {})
    results = session.pop('results', [])
    
    # テンプレートに渡す変数を設定
    category_name = form_data.get('category_keyword', '')
    filter_keyword = form_data.get('filter_keyword', '')
    limit = int(form_data.get('limit', 10))
    profit_margin = int(form_data.get('profit_margin', 15))
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
        pc_parts_categories=config.PC_PARTS_CATEGORIES,
        peripherals_categories=config.PERIPHERALS_CATEGORIES,
        makers_by_category_json=makers_by_category_json
    )

if __name__ == '__main__':
    # アプリケーション起動時に一度だけメーカーリストを読み込む
    preload_thread = threading.Thread(target=preload_maker_lists, daemon=True)
    preload_thread.start()
    app.run(host='0.0.0.0', port=5001, debug=False)
