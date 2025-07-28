import asyncio
import sys
from playwright.async_api import async_playwright
import urllib.parse

# Windowsのコンソールでの文字化け対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def scrape_tsukumo(search_keyword: str):
    """
    TSUKUMOで指定されたキーワードで検索し、商品情報を取得する関数
    """
    # URLエンコード
    encoded_keyword = urllib.parse.quote(search_keyword)
    url = f"https://shop.tsukumo.co.jp/search?end_of_sales=1&keyword={encoded_keyword}"
    
    print(f"TSUKUMOのスクレイピングを開始します: {url}")
    async with async_playwright() as p:
        # headless=Falseにするとブラウザの動きが見える
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()
        
        print("ページにアクセスします...")
        try:
            # ネットワークが安定するまで待つ
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"ページへのアクセスに失敗しました: {e}")
            await browser.close()
            return []

        print("アクセス完了。商品リストを探します...")

        # 商品リストの各アイテムを特定するセレクタ
        product_item_selector = "div.search-box__product"
        
        try:
            await page.wait_for_selector(product_item_selector, timeout=15000)
        except Exception:
            print("商品リストが見つかりませんでした。サイトの構造が変更された可能性があります。")
            await asyncio.sleep(5)
            await browser.close()
            return []
            
        product_elements = await page.query_selector_all(product_item_selector)
        
        if not product_elements:
            print("商品が見つかりませんでした。")
            await asyncio.sleep(5)
            await browser.close()
            return []

        print(f"{len(product_elements)}件の商品を検出しました。情報を抽出します。")
        
        results = []
        for item in product_elements:
            # 商品名
            name_element = await item.query_selector("h2.product-name")
            name = await name_element.inner_text() if name_element else "N/A"

            # 価格
            price_element = await item.query_selector("p.search-box__price span.text-red__common")
            price = await price_element.inner_text() if price_element else "N/A"
            
            # クリーニング
            name = name.strip()
            price = price.strip().replace('¥', '').replace(',', '').replace('(税込)', '')

            if name != "N/A" and price != "N/A":
                print(f"商品名: {name}")
                print(f"価格: {price}")
                print("-" * 20)
                results.append({"name": name, "price": price})

        await browser.close()
        print("TSUKUMOのスクレイピングが完了しました。")
        return results

async def main():
    # テスト用の検索キーワード
    test_keyword = "RTX 4070"
    
    print(f"テストを開始します... (キーワード: {test_keyword})")
    scraped_data = await scrape_tsukumo(test_keyword)
    if scraped_data:
        print("\n--- 取得成功 ---")
        print(f"合計 {len(scraped_data)}件のデータを取得できました。")
        # 最初の5件だけ表示
        print("\n取得データ（最初の5件）:")
        for item in scraped_data[:5]:
            print(item)
    else:
        print("\n--- 取得失敗 ---")
        print("データを取得できませんでした。")

if __name__ == '__main__':
    asyncio.run(main())
