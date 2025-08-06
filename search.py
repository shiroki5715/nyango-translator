import logging
import re
import urllib.parse
import concurrent.futures
from scrapers import kakaku, amazon

def _deduplicate_products(products: list) -> list:
    """
    製品リストから重複を排除する。
    製品名の最初の3要素をキーとし、価格が最も安いものを採用する。
    """
    log = logging.getLogger(__name__)
    log.info(f"取得した {len(products)} 件の製品から重複を排除します...")
    
    unique_products = {}
    for item in products:
        # 製品名からメーカー名 [〇〇] や【〇〇】を削除
        base_name = re.sub(r'[\[【].*?[\]】]', '', item['name']).strip()
        # 製品名をスペースで分割し、最初の3要素をキーとする
        product_key = ' '.join(base_name.split()[:3])

        # 辞書にキーが存在しないか、存在しても現在の価格の方が安い場合は登録/更新
        if product_key not in unique_products or item['price'] < unique_products[product_key]['price']:
            unique_products[product_key] = item
    
    deduplicated_list = list(unique_products.values())
    log.info(f"重複排除後、{len(deduplicated_list)} 件の製品が残りました。")
    return deduplicated_list

def _search_and_compare_for_maker(category_name, filter_keyword, limit, profit_margin, maker, sort):
    """
    単一のメーカーに対して価格.comとAmazonの価格を比較する内部関数
    """
    log = logging.getLogger(__name__)
    log.info(f"  -> メーカー '{maker}' の検索処理を開始...")
    
    # 価格.comから製品情報を取得
    kakaku_results = kakaku.scrape_products(
        category_name=category_name, 
        filter_keyword=filter_keyword, 
        limit=limit, 
        maker=maker, 
        sort=sort
    )
    
    if not kakaku_results:
        log.info(f"  -> メーカー '{maker}' の製品は見つかりませんでした。")
        return []

    # 重複排除
    deduplicated_results = _deduplicate_products(kakaku_results)

    maker_results = []
    for item in deduplicated_results:
        # 価格.comの商品名から主要な型番を抽出
        base_name = item['name'].split('[')[0].strip()

        # 抽出した型番でAmazonを検索
        amazon_result = amazon.scrape_product(base_name)
        
        if amazon_result:
            item['amazon_price'] = amazon_result.get('price')
            item['amazon_url'] = amazon_result.get('url')
        else:
            item['amazon_price'] = None
            item['amazon_url'] = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(base_name)}"
        
        # 利益計算
        if item.get('amazon_price') and item.get('price') and item.get('price') > 0:
            price_diff = item['amazon_price'] - item['price']
            margin = (price_diff / item['price']) * 100
            
            if margin >= profit_margin:
                item['price_difference'] = price_diff
                item['profit_margin'] = margin
                maker_results.append(item)
    
    log.info(f"  -> メーカー '{maker}' の処理完了。{len(maker_results)}件の利益商品を発見。")
    return maker_results

def run_search(category_name, filter_keyword, limit, profit_margin, makers, sort):
    """
    指定された条件で並列検索を実行し、結果を返す
    """
    log = logging.getLogger(__name__)
    log.info(f"検索リクエスト受信: カテゴリ='{category_name}', メーカー='{makers}', 1メーカーあたりの上限='{limit}'")
    
    all_results = []
    # 同時に実行する最大スレッド数を5に制限
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # 各メーカーに対する検索タスクを作成
        future_to_maker = {
            executor.submit(_search_and_compare_for_maker, category_name, filter_keyword, limit, profit_margin, maker, sort): maker 
            for maker in makers
        }
        # 完了したタスクから結果を取得
        for future in concurrent.futures.as_completed(future_to_maker):
            maker = future_to_maker[future]
            try:
                maker_results = future.result()
                all_results.extend(maker_results)
            except Exception as exc:
                log.error(f"メーカー '{maker}' の処理中にエラーが発生しました: {exc}", exc_info=True)
    
    # 利益率の高い順にソート
    sorted_results = sorted(all_results, key=lambda x: x.get('profit_margin', 0), reverse=True)
    return sorted_results
