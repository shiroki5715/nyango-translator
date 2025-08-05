# 共通ユーティリティ関数
import logging

def load_string_list_from_file(file_path: str) -> set:
    """
    指定されたファイルから1行ずつの文字列を読み込み、セットとして返す。
    空白文字は除去され、空行は無視される。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logging.warning(f"リストファイル '{file_path}' が見つかりません。")
        return set()
