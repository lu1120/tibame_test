 from bs4 import BeautifulSoup
import requests


def web_change(url)
# 1. 填入你在 Network 找到的 API 網址與參數
# 假設原網址包含 page=2，我們可以寫成迴圈來抓取多頁
#api_url = "https://imreadygo.com/category/%e5%8f%b0%e7%81%a3%e6%99%af%e9%bb%9e/"
api_url = url

    # 建議加上 User-Agent 模擬真人瀏覽器，避免被阻擋
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',

}
response = requests.get(api_url, headers=headers)

 # 2. 用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(response.text, "html.parser")

"""
# 假設我們要連續點擊 3 次「載入更多」（等於抓取第 2、3、4 頁）
for page in range(2, 5):
    params = {
        "page": page,
        "limit": 10
    }

    print(f"正在載入第 {page} 頁的更多資料...")
    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()  # 直接轉成 Python 字典/列表

        # 根據 JSON 結構抓取欄位（請依實際狀況修改）
        for item in data.get("posts", []):
            print(f"標題: {item.get('title')}")
            print(f"連結: {item.get('url')}")
            print("-" * 30)
    else:
        print(f"請求失敗，狀態碼：{response.status_code}")
        break
"""
num = 0
    
  # 範例 C：抓取多個相同標籤或清單
  # 假設要抓取所有文章連結 <a>
links = soup.find_all("div", class_="thumbnail")

for link in links:
    link_a = link.find('a')
    print(link_a.get("title"), link_a.get("href"))
    num+=1
print(num)

    
pages = soup.find_all("a",class_='page-numbers')
last_page = int(pages[-2].text)
print(last_page)

for page in range(2,last_page+1):
    api_url_new = f"https://imreadygo.com/category/%e5%8f%b0%e7%81%a3%e6%99%af%e9%bb%9e/page/{page}/"
    response = requests.get(api_url_new, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    print('ok')
    
    links = soup.find_all("div", class_="thumbnail")
    
    for link in links:
        link_a = link.find('a')
        print(link_a.get("title"), link_a.get("href"))
        num+=1
    print(num)