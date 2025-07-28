import asyncio
import sys
from playwright.async_api import async_playwright
import urllib.parse

# Windowsのコンソールでの文字化け対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def scrape_tsukumo(base_keyword: str, filter_keyword: str, limit: int):
    """
    TSUKUMOでキーワード検索し、指定件数に達するまでページを巡回しながら、
    さらに商品名で絞り込み、在庫のある商品だけを取得する関数
    """
    # ベースのキーワードと絞り込みキーワードを結合
    final_keyword = f"{base_keyword} {filter_keyword}".strip()
    encoded_keyword = urllib.parse.quote(final_keyword)
    start_url = f"https://shop.tsukumo.co.jp/search?end_of_sales=1&keyword={encoded_keyword}"
    
    print(f"TSUKUMO検索開始: キーワード='{final_keyword}', 目標件数={limit}")
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        current_url = start_url
        page_num = 1

        try:
            while current_url and len(results) < limit:
                print(f"{page_num}ページ目 ({len(results)}/{limit}件): {current_url}")
                await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                
                product_item_selector = "div.search-box__product"
                try:
                    await page.wait_for_selector(product_item_selector, timeout=10000)
                except Exception:
                    print("このページに商品が見つかりませんでした。")
                    break

                product_elements = await page.query_selector_all(product_item_selector)
                
                for item in product_elements:
                    # 在庫状況をチェック
                    stock_element = await item.query_selector("div.search_stock_title span")
                    stock_text = await stock_element.inner_text() if stock_element else ""
                    if "在庫なし" in stock_text or "販売終了" in stock_text or "入荷待ち" in stock_text:
                        continue

                    # 商品名を取得して、絞り込みキーワードが含まれているかチェック
                    name_container = await item.query_selector("span.search-box__product-name")
                    if not name_container: continue
                    link_element = await name_container.query_selector("a.product-link")
                    if not link_element: continue
                    name_element = await link_element.query_selector("h2.product-name")
                    if not name_element: continue
                    
                    name = await name_element.inner_text()
                    # 絞り込みキーワードが指定されている場合、商品名に含まれているかチェック (大文字小文字を無視)
                    if filter_keyword and filter_keyword.lower() not in name.lower():
                        continue

                    # 価格とURLを取得
                    price_element = await item.query_selector("p.search-box__price span.text-red__common")
                    if not price_element: continue
                    
                    price_text = await price_element.inner_text()
                    relative_url = await link_element.get_attribute('href')
                    price_str = price_text.strip().replace('¥', '').replace(',', '').replace('(税込)', '')

                    if name and price_str.isdigit() and relative_url:
                        full_url = urllib.parse.urljoin("https://shop.tsukumo.co.jp/", relative_url)
                        results.append({"name": name, "price": int(price_str), "url": full_url})
                        
                        # 目標件数に達したら、このページのループを抜ける
                        if len(results) >= limit:
                            break
                
                # 次のページへ
                if len(results) < limit:
                    next_button = await page.query_selector("a.c-pager__item--next")
                    if next_button:
                        next_page_path = await next_button.get_attribute("href")
                        current_url = urllib.parse.urljoin(current_url, next_page_path)
                        page_num += 1
                    else:
                        current_url = None # 次のページがなければ終了
                else:
                    current_url = None # 目標件数に達したら終了

            return results

        except Exception as e:
            print(f"TSUKUMOのスクレイピング全体でエラー: {e}")
            return results # 途中までの結果を返す
        finally:
            await browser.close()

async def scrape_amazon(product_name: str):
    """
    Amazonで指定された商品名を検索し、価格と商品URLを取得する関数
    """
    print(f"  Amazon検索: {product_name[:30]}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            search_url = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(product_name)}"
            await page.goto(search_url, timeout=60000)
            result_selector = 'div[data-component-type="s-search-result"]'
            await page.wait_for_selector(result_selector, timeout=10000)
            first_result = await page.query_selector(result_selector)
            if not first_result: return None
            price_element = await first_result.query_selector(".a-price-whole")
            url_element = await first_result.query_selector("a.a-link-normal")
            if price_element and url_element:
                price = int((await price_element.inner_text()).replace(',', ''))
                url = urllib.parse.urljoin("https://www.amazon.co.jp/", await url_element.get_attribute('href'))
                return {"price": price, "url": url}
            return None
        except Exception:
            return None
        finally:
            await browser.close()

if __name__ == '__main__':
    pass