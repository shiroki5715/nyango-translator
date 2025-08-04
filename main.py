import sys
import time
import urllib.parse
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

CATEGORY_URL_MAP = {
    # --- PCパーツ ---
    "CPU": "https://kakaku.com/specsearch/0510/",
    "CPUクーラー": "https://kakaku.com/specsearch/0512/",
    "メモリ": "https://kakaku.com/specsearch/0520/",
    "マザーボード": "https://kakaku.com/specsearch/0540/",
    "グラフィックボード": "https://kakaku.com/specsearch/0550/",
    "SSD": "https://kakaku.com/specsearch/0537/",
    "ハードディスク・HDD(3.5インチ)": "https://kakaku.com/specsearch/0530/",
    "ハードディスク・HDD(2.5インチ)": "https://kakaku.com/specsearch/0535/",
    "ハードディスク・HDD(SCSI)": "https://kakaku.com/specsearch/0536/",
    "PCケース": "https://kakaku.com/specsearch/0580/",
    "電源ユニット": "https://kakaku.com/specsearch/0590/",
    "サウンドカード": "https://kakaku.com/specsearch/0560/",
    "ケースファン": "https://kakaku.com/specsearch/0581/",
    "キャプチャーボード": "https://kakaku.com/specsearch/0568/",
    "DVDドライブ": "https://kakaku.com/specsearch/0125/",
    "ブルーレイドライブ": "https://kakaku.com/specsearch/0126/",
    # --- 周辺機器 ---
    "PCモニター・液晶ディスプレイ": "https://kakaku.com/specsearch/0085/",
    "VRゴーグル・VRヘッドセット": "https://kakaku.com/specsearch/0576/",
    "モニターアーム": "https://kakaku.com/specsearch/0086/",
    "プリンタ": "https://kakaku.com/specsearch/0060/",
    "スキャナ": "https://kakaku.com/specsearch/0070/",
    "マウス": "https://kakaku.com/specsearch/0160/",
    "キーボード": "https://kakaku.com/specsearch/0150/",
    "テンキー": "https://kakaku.com/specsearch/0153/",
    "WEBカメラ": "https://kakaku.com/specsearch/0567/",
    "NAS(ネットワークHDD)": "https://kakaku.com/specsearch/0538/",
    "無線LANルーター(Wi-Fiルーター)": "https://kakaku.com/specsearch/0077/",
}

def scrape_kakaku_com(category_name: str, filter_keyword: str = None, limit: int = 0, maker: str = None, sort: str = None):
    log = logging.getLogger(__name__)
    spec_search_url = CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
        return [], []

    log.info(f"価格.com処理開始: カテゴリ='{category_name}'")
    
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
                    
                    # 除外キーワードが含まれているかチェック
                    if any(keyword in name for keyword in EXCLUDED_KEYWORDS):
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

import requests

# --- 除外メーカーリストの読み込み ---
def load_excluded_makers(file_path: str) -> set:
    """指定されたファイルから除外メーカーのリストを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # ファイルから読み込んだ各行の空白文字を除去し、空行でなければセットに追加
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        # ファイルが存在しない場合は空のセットを返す
        logging.warning(f"除外メーカーリストファイル '{file_path}' が見つかりません。")
        return set()

# アプリケーション起動時に一度だけファイルを読み込む
EXCLUDED_MAKERS = load_excluded_makers('exclude_makers.txt')

# --- 除外キーワードリストの読み込み ---
def load_excluded_keywords(file_path: str) -> set:
    """指定されたファイルから除外キーワードのリストを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logging.warning(f"除外キーワードリストファイル '{file_path}' が見つかりません。")
        return set()

EXCLUDED_KEYWORDS = load_excluded_keywords('exclude_keywords.txt')


def get_makers_for_category(category_name: str):
    log = logging.getLogger(__name__)
    spec_search_url = CATEGORY_URL_MAP.get(category_name)
    if not spec_search_url:
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


def scrape_amazon(product_name: str):
    log = logging.getLogger(__name__)
    log.info(f"  Amazon検索: {product_name[:30]}...")
    driver = None
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

