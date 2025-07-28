import asyncio
import urllib.parse
from flask import Flask, render_template, request
from main import scrape_tsukumo, scrape_amazon

app = Flask(__name__)

async def search_and_compare(category_keyword, filter_keyword, limit, profit_margin):
    """
    TSUKUMOで検索し、結果をAmazon価格と比較し、利益率でフィルタリングする非同期関数
    """
    tsukumo_results = await scrape_tsukumo(category_keyword, filter_keyword, limit)
    
    if not tsukumo_results:
        return []

    target_items = tsukumo_results
    
    tasks = []
    for item in target_items:
        tasks.append(scrape_amazon(item['name']))
    
    amazon_results = await asyncio.gather(*tasks)

    filtered_results = []
    for i, item in enumerate(target_items):
        amazon_result = amazon_results[i]
        if amazon_result:
            item['amazon_price'] = amazon_result.get('price')
            item['amazon_url'] = amazon_result.get('url')
        else:
            item['amazon_price'] = None
            item['amazon_url'] = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(item['name'])}"

        # TSUKUMOとAmazonの両方で価格が取得できた場合のみ、利益率を計算
        if item.get('amazon_price') is not None and item.get('price') is not None and item.get('price') > 0:
            profit = item['amazon_price'] - item['price']
            margin = (profit / item['price']) * 100
            
            item['price_difference'] = profit
            item['profit_margin'] = margin  # 利益率をitemに追加
            
            if margin >= profit_margin:
                filtered_results.append(item)
        else:
            item['price_difference'] = None
            item['profit_margin'] = None # 計算できない場合もキーを追加

    return filtered_results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category_keyword = request.form.get('category_keyword', '')
        filter_keyword = request.form.get('filter_keyword', '')
        
        try:
            limit = int(request.form.get('limit', 5))
            profit_margin = int(request.form.get('profit_margin', 15))
        except (ValueError, TypeError):
            limit = 5
            profit_margin = 15
        
        if category_keyword:
            results = asyncio.run(search_and_compare(category_keyword, filter_keyword, limit, profit_margin))
            return render_template(
                'index.html', 
                results=results, 
                category_name=category_keyword, 
                filter_keyword=filter_keyword,
                limit=limit,
                profit_margin=profit_margin
            )
    
    return render_template(
        'index.html', 
        results=None, 
        category_name=None, 
        filter_keyword=None,
        limit=5,
        profit_margin=15
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
