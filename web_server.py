import asyncio
from flask import Flask, render_template, request
from main import scrape_tsukumo, scrape_amazon

app = Flask(__name__)

async def search_and_compare(keyword):
    """
    TSUKUMOで検索し、結果をAmazon価格と比較する非同期関数
    """
    tsukumo_results = await scrape_tsukumo(keyword)
    
    if not tsukumo_results:
        return []

    # 上位5件に絞ってAmazon検索を実行
    target_items = tsukumo_results[:5]
    
    tasks = []
    for item in target_items:
        tasks.append(scrape_amazon(item['name']))
    
    amazon_prices = await asyncio.gather(*tasks)

    for i, item in enumerate(target_items):
        amazon_price = amazon_prices[i]
        item['amazon_price'] = amazon_price
        if amazon_price is not None and item['price'] is not None:
            item['price_difference'] = amazon_price - item['price']
        else:
            item['price_difference'] = None

    return target_items

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form.get('category_keyword') # 'keyword' から変更
        if keyword:
            results = asyncio.run(search_and_compare(keyword))
            # 画面表示用に 'category_name' としてテンプレートに渡す
            return render_template('index.html', results=results, category_name=keyword)
    
    return render_template('index.html', results=None, category_name=None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
