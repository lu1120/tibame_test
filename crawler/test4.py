import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

options = webdriver.ChromeOptions()
# options.add_argument('--headless') # 視需要開啟
options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)

def web_scroll(url):
try:
    #target_url = "https://orange.udn.com/orange/cate/121191/121315"  # 💡 請替換成你的目標網址
    target_url = url  # 💡 請替換成你的目標網址
    driver.get(target_url)
    
    # 取得目前網頁的初始總高度
    last_height = driver.execute_script("return document.body.scrollHeight")

    scroll_count = 0
    while True:
    # 1. 執行 JavaScript 語法滾動到頁面最底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 2. 【極重要】一定要強制等待，留時間給伺服器回傳資料與網頁渲染
        time.sleep(2) 
    
    # 3. 取得滾動後的新網頁總高度
        new_height = driver.execute_script("return document.body.scrollHeight")
    
        scroll_count += 1
        print(f"第 {scroll_count} 次滾動，目前網頁高度：{new_height}")
    
    # 4. 比對新舊高度，如果相等，代表已經到底部，沒有新資料了
        if new_height == last_height:
            print("已經到達頁面最底部，停止滾動。")
            break
        
    # 5. 更新舊高度，繼續下一輪循環
        last_height = new_height
        
# # 滾動完成後，一次性獲取所有載入完畢的數據
#     items = driver.find_elements(By.CLASS_NAME, "your-item-class-name") # 替換為您的資料 Class 名稱
#     print(f"總共成功取得 {len(items)} 筆數據！")    
    
    
    # 4. 資料全部展開後，倒給 BeautifulSoup
    #print("\n--- 網頁擴展完成，開始用 BeautifulSoup 解析資料 ---")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 💡 在這裡寫你的 BeautifulSoup 解析邏輯
    # 範例：尋找所有的文章標題或商品名稱
  # 範例 C：抓取多個相同標籤或清單
  # 假設要抓取所有文章連結 <a>
    '''
    links = soup.find_all("div", class_="arrange_image")
    num = 0
    for link in links:
        link_a = link.find('a')
        print(link_a.get("title"), f'https:/{link_a.get("href")}')
        num += 1
    print(num)
    '''


finally:
    driver.quit()
    print("瀏覽器已關閉。")