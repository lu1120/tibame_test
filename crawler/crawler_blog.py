import time
import requests
from requests import options
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options


def web_btn_extend(url, num=100):
    #開啟瀏覽器控制
    options = Options()
    options.add_argument("--headless=new")  # Runs Chrome without a GUI
    options.add_argument("--no-sandbox")  # Bypasses OS security model layers
    options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
    driver = webdriver.Chrome(options=options)
    
    #嘗試完成點擊按鍵，延伸網頁
    try:
        target_url = url  # 💡 目標網址
        driver.get(target_url)
    
        click_limit = num  # 設定連續點擊幾次
        click_count = 0
    
        while click_count < click_limit:
            try:
                print(f"正在尋找第 {click_count + 1} 次按鈕...")

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

                # ⏳ 等待新資料載入
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
        
        #擷取網頁資料(一次全部)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        num = 0  #資料計數
        dict_list = {} #存放資料對
        links = soup.find_all("a", class_="full-cover-link")
        
        for link in links:
            print(link.get("title"), link.get("href"))
            dict_list[link.get("title")] = link.get("href")
            num += 1
        
        return dict_list
        print(num)
        
    finally:
        driver.quit()
        print("瀏覽器已關閉。")
        
def web_scroll(url,num = 100):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # 視需要開啟
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    
    #開啟瀏覽器控制
    # options = Options()
    # options.add_argument("--headless=new")  # Runs Chrome without a GUI
    # options.add_argument("--no-sandbox")  # Bypasses OS security model layers
    # options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
    # driver = webdriver.Chrome(options=options)
    
    try:
        #target_url = "https://orange.udn.com/orange/cate/121191/121315"  # 💡 請替換成你的目標網址
        target_url = url  # 💡 請替換成你的目標網址
        driver.get(target_url)
    
        # 取得目前網頁的初始總高度
        last_height = driver.execute_script("return document.body.scrollHeight")

        scroll_count = 0
        while True:
            # 滾動到頁面最底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
            # 等待回傳資料與網頁渲染
            time.sleep(2) 
        
            # 取得滾動後的新網頁總高度
            new_height = driver.execute_script("return document.body.scrollHeight")
        
            scroll_count += 1
            print(f"第 {scroll_count} 次滾動，目前網頁高度：{new_height}")

            #一定次數後終止
            if scroll_count == num:
                print(f"已經滾動 {num} 次，停止滾動。")
                break
            
            # 比對新舊高度，如果相等，代表已經到底部，沒有新資料了
            if new_height == last_height:
                print("已經到達頁面最底部，停止滾動。")
                break
            
            # 5. 更新舊高度，繼續下一輪循環
            last_height = new_height
        print('已經載入全部資料')
        
        #擷取網頁資料(一次全部)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        num = 0  #資料計數
        dict_list = {} #存放資料對
        links = soup.find_all("div", class_="arrange_image")
        
        for link in links:
            link_a = link.find('a')
            print(link_a.get("title"), f'https:/{link_a.get("href")}')
            dict_list[link_a.get("title")] = f'https:/{link_a.get("href")}'
            num += 1
        return dict_list
        print(num)
    
    finally:
        driver.quit()
        print("瀏覽器已關閉。")
        
def web_changePage(url):
        
    # 填入你在 Network 找到的 API 網址與參數
    # 假設原網址包含 page=2，我們可以寫成迴圈來抓取多頁
    #api_url = "https://imreadygo.com/category/%e5%8f%b0%e7%81%a3%e6%99%af%e9%bb%9e/"
    api_url = url

    # 建議加上 User-Agent 模擬真人瀏覽器，避免被阻擋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
    }
    response = requests.get(api_url, headers=headers)

    # 用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 第一次抓資料(第一頁網址通常與後面網址有出入)
    num = 0
    dict_list = {}
    
    links = soup.find_all("div", class_="thumbnail")

    for link in links:
        link_a = link.find('a')
        print(link_a.get("title"), link_a.get("href"))
        dict_list[link_a.get("title")] = link_a.get("href")
        num+=1
    print(num)

    # 找到總共幾頁
    pages = soup.find_all("a",class_='page-numbers')
    last_page = int(pages[-2].text)
    print(f"總共有{last_page}頁")

    # 開始循頁，抓取資料
    for page in range(2,last_page+1):
        api_url_new = f"https://imreadygo.com/category/%e5%8f%b0%e7%81%a3%e6%99%af%e9%bb%9e/page/{page}/" #新網址
        response_new = requests.get(api_url_new, headers=headers)
        soup_new = BeautifulSoup(response_new.text, "html.parser")
        
        links_new = soup_new.find_all("div", class_="thumbnail")
        
        for link_new in links_new:
            link_new_a = link_new.find('a')
            print(link_new_a.get("title"), link_new_a.get("href"))
            dict_list[link_new_a.get("title")] = link_new_a.get("href")
            num+=1
        print(num)
    print('全部資料抓取完成')        
    
    
def web_pageNext(url, page = 100):
    
    api_url = url
    num = 0
    count = 0
    item_list = []

    while True:    
        # 填入你在 Network 找到的 API 網址與參數
    # 假設原網址包含 page=2，我們可以寫成迴圈來抓取多頁
    #api_url = "https://imreadygo.com/category/%e5%8f%b0%e7%81%a3%e6%99%af%e9%bb%9e/"
    #api_url = url

    # 建議加上 User-Agent 模擬真人瀏覽器，避免被阻擋
        headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
        }
        response = requests.get(api_url, headers=headers, verify=False)

    # 用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 第一次抓資料(第一頁網址通常與後面網址有出入)


        url_d = soup.find_all("td")
        for i in url_d:
            print(i.find('div').text.split(':')[-1])
            item_list.append(i.find('div').text.split(':')[-1])
            num+=1
        print(num)
        count+=1

        nextPage = soup.find("li", class_="mr-1 PagedList-skipToNext")
        nextPage_a = nextPage.find('a').get("href")
        api_url = f"https://media.taiwan.net.tw{nextPage_a}"
        
        if count == page:
            break
     
    print('全部資料抓取完成')    
    return item_list

        
