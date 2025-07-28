import asyncio
import urllib.parse
from flask import Flask, render_template, request
from main import scrape_tsukumo, scrape_amazon

app = Flask(__name__)

async def search_and_compare(category_keyword, filter_keyword, limit):
    """
    TSUKUMOで検索し、結果をAmazon価格と比較する非同期関数
    """
    # 新しいscrape_tsukumo関数を呼び出す
    tsukumo_results = await scrape_tsukumo(category_keyword, filter_keyword, limit)
    
    if not tsukumo_results:
        return []

    # Amazon検索は、TSUKUMOで見つかった商品に対してのみ実行
    target_items = tsukumo_results
    
    tasks = []
    for item in target_items:
        tasks.append(scrape_amazon(item['name']))
    
    amazon_results = await asyncio.gather(*tasks)

    for i, item in enumerate(target_items):
        amazon_result = amazon_results[i]
        if amazon_result:
            item['amazon_price'] = amazon_result.get('price')
            item['amazon_url'] = amazon_result.get('url')
        else:
            item['amazon_price'] = None
            item['amazon_url'] = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(item['name'])}"

        if item.get('amazon_price') is not None and item.get('price') is not None:
            item['price_difference'] = item['amazon_price'] - item['price']
        else:
            item['price_difference'] = None

    return target_items

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category_keyword = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        
        try:
            limit = int(request.form.get('limit', 5))
        except (ValueError, TypeError):
            limit = 5
        
        if category_keyword:
            # 新しい引数でsearch_and_compareを呼び出す
            results = asyncio.run(search_and_compare(category_keyword, filter_keyword, limit))
            return render_template(
                'index.html', 
                results=results, 
                category_name=category_keyword, 
                filter_keyword=filter_keyword,
                limit=limit
            )
    
    return render_template(
        'index.html', 
        results=None, 
        category_name=None, 
        filter_keyword=None,
        limit=5
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')