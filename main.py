import sys
import time
import urllib.parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Windowsのコンソールでの文字化け対策
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# カテゴリ名と、最終目的地の「スペック検索ページ」の正しいURLを対応させる
CATEGORY_URL_MAP = {
    "グラフィックボード": "https://kakaku.com/specsearch/0550/",
    "マザーボード": "https://kakaku.com/specsearch/0540/",
    "SSD": "https://kakaku.com/specsearch/0537/",
    "メモリ": "https://kakaku.com/specsearch/0520/",
    "CPU": "https://kakaku.com/specsearch/0510/",
    "PCケース": "https://kakaku.com/specsearch/0580/",
    "電源ユニット": "https://kakaku.com/specsearch/0590/",
    "キーボード": "https://kakaku.com/specsearch/0150/",
    "マウス": "https://kakaku.com/specsearch/0160/",
    "液晶モニター": "https://kakaku.com/specsearch/0085/",
}

def scrape_kakaku_com(category_name: str, filter_keyword: str, limit: int):
    """
    undetected-chromedriverを使い、正しいスペック検索ページに直接アクセスして情報を取得する
    """
    spec_search_url = CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
        print(f"エラー: '{category_name}' に対応するURLが見つかりません。")
        return []

    print(f"価格.com検索開始 (正しいURL): カテゴリ='{category_name}'")
    
    results = []
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless') 
        driver = uc.Chrome(options=options)
        
        print(f"Step 1: スペック検索ページへ直接移動します -> {spec_search_url}")
        driver.get(spec_search_url)
        
        # --- デバッグ：ページのHTMLを保存 ---
        print("DEBUG: ページに到着しました。HTMLを 'last_page.html' に保存します。")
        with open("last_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("DEBUG: HTMLの保存が完了しました。")

        # --- Step 2: ページ巡回と情報収集 ---
        print("Step 2: ページ巡回を開始します...")
        wait = WebDriverWait(driver, 15)
        page_num = 1
        
        while len(results) < limit:
            print(f"  {page_num}ページ目 ({len(results)}/{limit}件)")
            
            # テーブルが表示されるまで待つ (絶対的な正解のセレクタ)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#spec_result table.tblBorderGray02")))
            
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'lxml')
            # 絶対的な正解のセレクタで、商品情報が含まれる行(tr)を全て取得
            product_rows = soup.select("#spec_result table.tblBorderGray02 tr")

            for row in product_rows:
                # ヘッダー行はクラス名(bgColor02 or bgColor03)を持っているので、それらを除外する
                if row.get('class') and ('bgColor02' in row.get('class') or 'bgColor03' in row.get('class')):
                    continue
                
                if len(results) >= limit: break

                name_element = row.select_one("td.textL a") # より正確なセレクタに変更
                price_element = row.select_one("span.priceText a") # より正確なセレクタに変更

                if name_element and price_element:
                    name = name_element.get_text(strip=True)
                    price_text = price_element.get_text(strip=True).replace('¥', '').replace(',', '')
                    relative_url = name_element.get('href')

                    if filter_keyword and filter_keyword.lower() not in name.lower():
                        continue

                    if name and price_text.isdigit() and relative_url:
                        full_url = urllib.parse.urljoin("https://kakaku.com/", relative_url)
                        results.append({"name": name, "price": int(price_text), "url": full_url})
            
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.pagerNext")
                print("    -> 次のページへ")
                driver.execute_script("arguments[0].click();", next_button)
                page_num += 1
                time.sleep(2)
            except:
                print("次のページは見つかりませんでした。")
                break

        return results

    except Exception as e:
        print(f"スクレイピングでエラーが発生しました: {e}")
        return results
    finally:
        if driver:
            print("ブラウザを閉じます。")
            driver.quit()

def scrape_amazon(product_name: str):
    print(f"  Amazon検索: {product_name[:30]}...")
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        search_url = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(product_name)}"
        driver.get(search_url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))
        
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'lxml')

        first_result = soup.select_one('div[data-component-type="s-search-result"]')
        if not first_result: return None

        price_element = first_result.select_one(".a-price-whole")
        url_element = first_result.select_one("a.a-link-normal")

        if price_element and url_element:
            price = int(price_element.get_text(strip=True).replace(',', ''))
            url = urllib.parse.urljoin("https://www.amazon.co.jp/", url_element.get('href'))
            return {"price": price, "url": url}
        return None
    except Exception:
        return None
    finally:
        if driver:
            driver.quit()

if __name__ == '__main__':
    pass
