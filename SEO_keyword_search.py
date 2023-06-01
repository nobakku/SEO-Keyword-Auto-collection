import re
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By

# WebDriverを自動更新するwebdriver_managerを追加
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))



# Googleのトップページ
URL = "https://www.google.co.jp"



# 全体の処理
def main():
    """
    メインの処理
    Googleの検索エンジンでキーワードを検索
    指定されたドメインが検索結果の１ページ目に含まれていないキーワードをテキストファイルに出力
    """
    # １行ずつ読み込んで改行コードを削除してリストにする
    with open('検索キーワードリスト.txt', encoding="utf-8") as f:
        keywords = [s.rstrip() for s in f.readlines()]
    with open('ドメインリスト.txt', encoding="utf-8") as f:
        domains = [s.rstrip() for s in f.readlines()]

    # Googleのトップページを開く
    driver.get(URL)
    time.sleep(2)

    ok_keyword_list = []

    # 全体をまとめた処理
    for keyword in keywords:
        search(keyword, driver)
        urls = get_url(driver)
        weak_keyword_list = domain_checked(urls, domains, ok_keyword_list, keyword)

    # 'result.txt'という名前を付けて、ドメインチェックしたキーワードをファイルに書き込む
    with open('result.txt', 'w') as f:
        f.write('\n'.join(weak_keyword_list))  # ドメインチェック済みのキーワードを１行ずつ保存
    # ブラウザーを閉じる
    driver.quit()


# Chrome操作
def search(keyword, driver):
    """
    検索テキストボックスに検索キーワードを入力し、検索する
    """
    # 検索テキストボックスの要素をname属性から取得
    input_element = driver.find_element(By.NAME,"q")
    # 検索テキストボックスに入力されている文字列を消去
    input_element.clear()
    # 検索テキストボックスにキーワードを入力
    input_element.send_keys(keyword)
    # Enterキーを送信
    input_element.send_keys(Keys.RETURN)
    time.sleep(2)


# URL取得
def get_url(driver):
    """
    検索結果ページの1位から10位までのURLを取得
    """
    # 各ページのURLを入れるためのリストを指定
    urls = []
    # a要素（各ページの1位から10位までのURL）取得
    objects = driver.find_elements(By.CSS_SELECTOR, 'div.Z26q7c.UK95Uc.jGGQ5e > div > a')

    # 各ページのURLをリストに追加
    if objects:
        for object in objects:
            urls.append(object.get_attribute('href'))
    else:
        print('URLが取得できませんでした。')
    return urls


# ドメインチェック
def domain_checked(urls, domains, ok_keyword_list, keyword):
    """
    URLリストからドメインを取得し、指定ドメインに含まれているかチェック
    """
    # 上で取り出したリストのURLの形は https://abcd.com/ や https://www.abcd.com/ がある。
    # URLリストから各ページのURLを１つずつ取り出す
    for url in urls:
        # '//〇〇/'に一致する箇所（ドメイン）を抜き出す
        m = re.search(r'//(.*?)/', url)
        domain = m.group(1)
        if 'www.' in domain:
            # 含まれているなら'www.'を除去
            domain = domain[4:]
        # 各ページのドメインが指定ドメインに含まれているかチェック
        if domain in domains:
            print(f'キーワード「{keyword}」の検索結果には大手ドメインがありましたので除外します。')
            break  # １つでも含まれているなら他はチェックする必要がないので関数を終了
    else:
        # 指定ドメインに含まれていないならキーワードをok_keyword_listに追加
        ok_keyword_list.append(keyword)
    return ok_keyword_list


if __name__ == "__main__":
    main()
