import time
import urllib.parse
import logging
import requests
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import config
import utils

# --- 除外リストの読み込み ---
EXCLUDED_MAKERS = utils.load_string_list_from_file(config.EXCLUDED_MAKERS_FILE)
EXCLUDED_KEYWORDS = utils.load_string_list_from_file(config.EXCLUDED_KEYWORDS_FILE)


def scrape_products(category_name: str, filter_keyword: str = None, limit: int = 0, maker: str = None, sort: str = None):
    """
    価格.comから指定されたカテゴリの製品情報をスクレイピングする
    """
    log = logging.getLogger(__name__)
    spec_search_url = config.CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
        log.warning(f"カテゴリ '{category_name}' のURLが見つかりません。")
        return []

    log.info(f"価格.com処理開始: カテゴリ='{category_name}', メーカー='{maker}'")
    
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        
        driver.get(spec_search_url)
        
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

            if not product_rows:
                log.info("製品リストが見つかりませんでした。")
                break

            for row in product_rows:
                if len(results) >= limit:
                    break
                # ヘッダー行などをスキップ
                if row.get('class') and ('bgColor02' in row.get('class') or 'bgColor03' in row.get('class')):
                    continue
                
                name_element = row.select_one("td.textL a")
                price_element = row.select_one("span.priceText a")
                
                if name_element and price_element:
                    name = name_element.get_text(strip=True)
                    price_text = price_element.get_text(strip=True).replace('¥', '').replace(',', '')
                    relative_url = name_element.get('href')
                    
                    # 絞り込みキーワードのチェック
                    if filter_keyword and filter_keyword.lower() not in name.lower():
                        continue
                    
                    # 除外キーワードのチェック
                    if any(keyword in name for keyword in EXCLUDED_KEYWORDS):
                        continue

                    if name and price_text.isdigit() and relative_url:
                        full_url = urllib.parse.urljoin("https://kakaku.com/", relative_url)
                        results.append({"name": name, "price": int(price_text), "url": full_url})
            
            # 「次へ」ボタンが存在するか確認してクリック
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.pagerNext")
                driver.execute_script("arguments[0].click();", next_button)
                log.info(f"{page_num}ページ目を取得。現在{len(results)}件。")
                page_num += 1
                time.sleep(2)  # サーバー負荷軽減
            except:
                log.info("次のページが見つかりませんでした。処理を終了します。")
                break
        
        log.info(f"価格.com処理完了。{len(results)}件の製品情報を取得しました。")
        return results

    except Exception as e:
        log.error(f"スクレイピングで致命的なエラーが発生: {e}", exc_info=True)
        return []
    finally:
        if driver:
            driver.quit()


def get_makers(category_name: str):
    """
    価格.comから指定されたカテゴリのメーカーリストを取得する
    """
    log = logging.getLogger(__name__)
    spec_search_url = config.CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
        log.warning(f"カテゴリ '{category_name}' のURLが見つかりません。")
        return []

    log.info(f"メーカーリスト取得開始: カテゴリ='{category_name}'")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        response = requests.get(spec_search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        maker_select_element = soup.find("select", {"name": "LstMaker"})
        if not maker_select_element:
            log.warning(f"  -> {category_name} のメーカー選択リストが見つかりませんでした。")
            return []

        makers = [
            option.get_text(strip=True) 
            for option in maker_select_element.find_all("option") 
            if option.get("value") and option.get_text(strip=True) not in EXCLUDED_MAKERS
        ]
        log.info(f"  -> {category_name} のメーカーを {len(makers)} 件取得しました。")
        return makers

    except requests.exceptions.RequestException as e:
        log.error(f"メーカーリスト取得でHTTPエラーが発生: {e}", exc_info=True)
        return []
    except Exception as e:
        log.error(f"メーカーリスト取得で予期せぬエラーが発生: {e}", exc_info=True)
        return []
