import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# options = webdriver.ChromeOptions()
# # options.add_argument('--headless') # 視需要開啟
# options.add_argument('--start-maximized')

# driver = webdriver.Chrome(options=options)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")  # Runs Chrome without a GUI
options.add_argument("--no-sandbox")  # Bypasses OS security model layers
options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems

driver = webdriver.Chrome(options=options)

def web_extention(url,pages=10):
    try:
        target_url = url  # 💡 請替換成你的目標網址
        driver.get(target_url)

        click_limit = pages  # 設定你想連續點擊幾次
        click_count = 0

        while click_count < click_limit:
            try:
                print(f"正在尋找第 {click_count + 1} 次『Load More』按鈕...")

                # 🎯 精準定位：直接使用該標籤的 id
                load_more_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "mk_load_more_button"))
                )

                # 捲動畫面到按鈕的正中央，避免被其他置底選單或廣告遮擋
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
                time.sleep(0.5)

                # 執行點擊
                load_more_btn.click()
                print(f"✅ 成功點擊第 {click_count + 1} 次！")
                click_count += 1

                # ⏳ 重要：點擊後網頁會出現載入動畫（mk-loading-indicator），需等待新資料載入
                time.sleep(2.5)

            except TimeoutException:
                print("【提示】找不到按鈕。可能已經載入全部資料，或是按鈕已隱藏。")
                break
            except ElementClickInterceptedException:
                # 如果按鈕正在「載入中」或是被遮擋，改用 JS 強制點擊
                print("【警告】按鈕暫時無法直接點擊（可能正在Loading中），嘗試使用 JS 強制觸發...")
                driver.execute_script("arguments.click();", load_more_btn)
                click_count += 1
                time.sleep(2.5)
            except Exception as e:
                print(f"發生其他未知錯誤: {e}")
                break
        print('已經載入全部資料')

    # 4. 資料全部展開後，倒給 BeautifulSoup
    #print("\n--- 網頁擴展完成，開始用 BeautifulSoup 解析資料 ---")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 💡 在這裡寫你的 BeautifulSoup 解析邏輯
    # 範例：尋找所有的文章標題或商品名稱
  # 範例 C：抓取多個相同標籤或清單
  # 假設要抓取所有文章連結 <a>
    """
    links = soup.find_all("a", class_="full-cover-link")
    num = 0
    for link in links:
        print(link.get("title"), link.get("href"))
        num += 1
    print(num)
    """

finally:
    driver.quit()
    print("瀏覽器已關閉。")