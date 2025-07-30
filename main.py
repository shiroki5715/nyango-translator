import sys
import time
import urllib.parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

CATEGORY_URL_MAP = {
    "CPU": "https://kakaku.com/specsearch/0510/",
    "CPUクーラー": "https://kakaku.com/specsearch/0512/",
    "メモリ": "https://kakaku.com/specsearch/0520/",
    "マザーボード": "https://kakaku.com/specsearch/0540/",
    "グラフィックボード": "https://kakaku.com/specsearch/0550/",
    "SSD": "https://kakaku.com/specsearch/0537/",
    "ハードディスク・HDD(3.5インチ)": "https://kakaku.com/specsearch/0530/",
    "ハードディスク・HDD(2.5インチ)": "https://kakaku.com/specsearch/0535/",
    "PCケース": "https://kakaku.com/specsearch/0580/",
    "電源ユニット": "https://kakaku.com/specsearch/0590/",
    "サウンドカード": "https://kakaku.com/specsearch/0560/",
    "ケースファン": "https://kakaku.com/specsearch/0581/",
    "ファンコントローラー": "https://kakaku.com/specsearch/0582/",
    "インターフェイスカード": "https://kakaku.com/specsearch/0565/",
    "キャプチャーボード": "https://kakaku.com/specsearch/0568/",
    "ハードディスク ケース": "https://kakaku.com/specsearch/0539/",
    "リムーバブルケース": "https://kakaku.com/specsearch/0543/",
    "DVDドライブ": "https://kakaku.com/specsearch/0125/",
    "ブルーレイドライブ": "https://kakaku.com/specsearch/0126/",
    "液晶モニター": "https://kakaku.com/specsearch/0085/",
    "キーボード": "https://kakaku.com/specsearch/0150/",
    "マウス": "https://kakaku.com/specsearch/0160/",
    "NAS(ネットワークHDD)": "https://kakaku.com/specsearch/0538/",
    "無線LANルーター(Wi-Fiルーター)": "https://kakaku.com/specsearch/0077/",
}

def scrape_kakaku_com(category_name: str, filter_keyword: str = None, limit: int = 0, maker: str = None, sort: str = None, get_makers_only: bool = False):
    log = logging.getLogger(__name__)
    spec_search_url = CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
        return [], []

    log.info(f"価格.com処理開始: カテゴリ='{category_name}', メーカーリスト取得={get_makers_only}")
    
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        
        driver.get(spec_search_url)
        
        if get_makers_only:
            maker_select_element = wait.until(EC.presence_of_element_located((By.NAME, "LstMaker")))
            select = Select(maker_select_element)
            makers = [option.text for option in select.options if option.get_attribute("value")]
            log.info(f"  -> {category_name} のメーカーを {len(makers)} 件取得しました。")
            return [], makers

        if maker:
            maker_select = Select(wait.until(EC.element_to_be_clickable((By.NAME, "LstMaker"))))
            maker_select.select_by_visible_text(maker)

        if sort:
            sort_select = Select(wait.until(EC.element_to_be_clickable((By.NAME, "Sort"))))
            sort_select.select_by_value(sort)
        
        driver.find_element(By.CSS_SELECTOR, 'input[type="image"][value="検索する"]').click()
        
        results = []
        page_num = 1
        while len(results) < limit:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#spec_result table.tblBorderGray02")))
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'lxml')
            product_rows = soup.select("#spec_result table.tblBorderGray02 tr")

            for row in product_rows:
                if row.get('class') and ('bgColor02' in row.get('class') or 'bgColor03' in row.get('class')):
                    continue
                if len(results) >= limit: break
                name_element = row.select_one("td.textL a")
                price_element = row.select_one("span.priceText a")
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
                driver.execute_script("arguments[0].click();", next_button)
                page_num += 1
                time.sleep(2)
            except:
                break
        return results, []

    except Exception as e:
        log.error(f"スクレイピングで致命的なエラーが発生: {e}", exc_info=True)
        return [], []
    finally:
        if driver:
            driver.quit()

def scrape_amazon(product_name: str):
    log = logging.getLogger(__name__)
    log.info(f"  Amazon検索: {product_name[:30]}...")
    driver = None
    for attempt in range(2):
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
            if not first_result:
                time.sleep(3)
                continue
            price_element = first_result.select_one(".a-price-whole")
            url_element = first_result.select_one("a.a-link-normal")
            if price_element and url_element:
                price = int(price_element.get_text(strip=True).replace(',', ''))
                url = urllib.parse.urljoin("https://www.amazon.co.jp/", url_element.get('href'))
                return {"price": price, "url": url}
            else:
                time.sleep(3)
                continue
        except Exception as e:
            log.warning(f"    Attempt {attempt + 1}: Amazon検索中にエラー: {e}")
            time.sleep(3)
        finally:
            if driver:
                driver.quit()
    log.error(f"  -> Amazon検索失敗: {product_name[:30]}...")
    return None
