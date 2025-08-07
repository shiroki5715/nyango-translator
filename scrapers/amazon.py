import time
import urllib.parse
import logging
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_product(product_name: str):
    """
    Amazon.co.jpで指定された製品名で検索し、最初の検索結果の価格とURLを取得する
    """
    log = logging.getLogger(__name__)
    log.info(f"  Amazon検索: {product_name[:30]}...")
    
    driver = None
    # 2回までリトライ
    for attempt in range(2):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920x1080')
            driver = webdriver.Chrome(options=options)
            
            search_url = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(product_name)}"
            driver.get(search_url)
            
            # 検索結果が表示されるまで待機
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')))
            
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 最初の検索結果を取得
            first_result = soup.select_one('div[data-component-type="s-search-result"]')
            
            if not first_result:
                log.warning(f"    Attempt {attempt + 1}: 検索結果が見つかりませんでした。")
                time.sleep(3) # 少し待ってリトライ
                continue
                
            price_element = first_result.select_one(".a-price-whole")
            # a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal
            url_element = first_result.select_one("a.a-link-normal.s-underline-text")
            
            if price_element and url_element:
                price = int(price_element.get_text(strip=True).replace(',', ''))
                url = urllib.parse.urljoin("https://www.amazon.co.jp/", url_element.get('href'))
                # URLからフラグメント（#以降）を削除
                url = url.split('#')[0]
                log.info(f"    -> Amazon価格: ¥{price:,}")
                return {"price": price, "url": url}
            else:
                log.warning(f"    Attempt {attempt + 1}: 価格またはURLが見つかりませんでした。")
                time.sleep(3) # 少し待ってリトライ
                continue

        except Exception as e:
            log.warning(f"    Attempt {attempt + 1}: Amazon検索中にエラー: {e}")
            time.sleep(3) # エラー発生時も待機
        finally:
            if driver:
                driver.quit()
                
    log.error(f"  -> Amazon検索失敗: {product_name[:30]}...")
    return None
