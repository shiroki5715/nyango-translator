from flask import Flask, render_template, request
import urllib.parse
from main import scrape_kakaku_com, scrape_amazon

app = Flask(__name__)

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
            # 最もシンプルな形で、直接関数を呼び出す
            print("--- 検索処理を開始します ---")
            kakaku_results = scrape_kakaku_com(category_keyword, filter_keyword, limit)
            
            final_results = []
            if kakaku_results:
                print(f"--- 価格.comから {len(kakaku_results)} 件取得。Amazonでの検索を開始します ---")
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
                            final_results.append(item)
                    else:
                        item['price_difference'] = None
                        item['profit_margin'] = None
            
            print(f"--- 全ての処理が完了しました。{len(final_results)} 件の結果を返します ---")
            return render_template(
                'index.html', 
                results=final_results, 
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
    app.run(host='0.0.0.0', port=5000, debug=False)