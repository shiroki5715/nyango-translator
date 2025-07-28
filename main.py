import asyncio
import sys
import random
from playwright.async_api import async_playwright
import urllib.parse

# Windowsのコンソールでの文字化け対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def scrape_tsukumo_category(category_url: str):
    """
    TSUKUMOの指定されたカテゴリページから全商品情報を取得する関数（ページネーション・ブロック回避対応）
    """
    print(f"TSUKUMOのカテゴリページをスクレイピングします: {category_url}")
    results = []
    
    async with async_playwright() as p:
        # --- ブロック回避策 ---
        browser = await p.chromium.launch(
            headless=False, # ブラウザを表示して人間らしいアクセスを偽装
            channel="chrome", # 通常のChromeを利用
            args=['--disable-blink-features=AutomationControlled'] # 自動化検知を無効化
        )
        page = await browser.new_page()
        
        current_url = category_url
        page_num = 1

        while current_url:
            print(f"{page_num}ページ目にアクセスします: {current_url}")
            try:
                await asyncio.sleep(random.uniform(2, 5))
                await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)

                # Cookie同意ボタンが表示されていればクリック
                cookie_button_selector = "#onetrust-accept-btn-handler"
                try:
                    await page.wait_for_selector(cookie_button_selector, timeout=5000)
                    await page.click(cookie_button_selector)
                    print("Cookie同意ボタンをクリックしました。")
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    print("Cookie同意ボタンは見つかりませんでした。")

                # 商品リストが表示されるまで待機
                product_item_selector = "div.product-box__item"
                await page.wait_for_selector(product_item_selector, timeout=15000)
                
            except Exception as e:
                print(f"ページへのアクセスまたは要素の待機に失敗しました: {e}")
                break
                
            product_elements = await page.query_selector_all(product_item_selector)
            if not product_elements:
                print("このページに商品が見つかりませんでした。")
                break

            print(f"{len(product_elements)}件の商品を検出しました。")
            
            for item in product_elements:
                name_element = await item.query_selector("p.product-box__product-name a")
                name = await name_element.inner_text() if name_element else "N/A"
                
                price_element = await item.query_selector("p.product-box__price-regular")
                price = await price_element.inner_text() if price_element else "N/A"
                
                url_element = await item.query_selector("p.product-box__product-name a")
                product_url = await url_element.get_attribute('href') if url_element else ""

                name = name.strip()
                price_str = price.strip().replace('¥', '').replace(',', '').replace('(税込)', '')

                if name != "N/A" and price_str.isdigit():
                    full_url = urllib.parse.urljoin("https://shop.tsukumo.co.jp/", product_url)
                    results.append({"name": name, "price": int(price_str), "url": full_url})

            # 「次へ」ボタンを探す
            next_button = await page.query_selector("a.c-pager__item--next")
            if next_button:
                next_page_path = await next_button.get_attribute("href")
                current_url = urllib.parse.urljoin(current_url, next_page_path)
                page_num += 1
            else:
                current_url = None

        await browser.close()
        print(f"TSUKUMOのスクレイピング完了。合計{len(results)}件取得。")
        return results


async def scrape_amazon(product_name: str):
    """
    Amazonで指定された商品名を検索し、価格を取得する関数
    """
    print(f"Amazonで「{product_name}」を検索します...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # こちらも念のため表示
        page = await browser.new_page()

        try:
            await asyncio.sleep(random.uniform(1, 3))
            await page.goto("https://www.amazon.co.jp/", timeout=60000)
            
            await page.fill("#twotabsearchtextbox", product_name)
            await page.press("#twotabsearchtextbox", "Enter")
            
            await page.wait_for_load_state("domcontentloaded", timeout=60000)

            price_selector = 'div[data-component-type="s-search-result"] .a-price-whole'
            
            await page.wait_for_selector(price_selector, timeout=10000)
            price_element = await page.query_selector(price_selector)
            
            if price_element:
                price_text = await price_element.inner_text()
                price = int(price_text.replace(',', ''))
                print(f"Amazon価格: ¥{price:,}")
                return price
            else:
                return None
        except Exception as e:
            print(f"Amazonのスクレイピング中にエラー: {e}")
            return None
        finally:
            await browser.close()

if __name__ == '__main__':
    # テスト実行用のコード（直接実行用）
    async def test_run():
        # test_url = "https://shop.tsukumo.co.jp/search/c:101520/" # SSD
        test_url = "https://shop.tsukumo.co.jp/search/c:101010/" # マザーボード
        data = await scrape_tsukumo_category(test_url)
        if data:
            print("\n--- 取得データ (最初の5件) ---")
            for item in data[:5]:
                print(item)
    
    asyncio.run(test_run())