from fileinput import filename
import os
from urllib import response
from urllib.parse import quote_plus, urlparse  # 密碼含 @ : % 等符號時要先做 URL 編碼才能進連線字串
from bs4 import BeautifulSoup
import pandas as pd
import requests
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）

from crawler.config import (
    GCP_PROJECT_ID,
    MYSQL_ACCOUNT,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    SPANNER_INSTANCE,
)
import json
from crawler.worker import app
from crawler.crawler_tdx import get_tdx_token, get_tdx_title
from crawler.crawler_blog import web_pageNext
from crawler.get_data import dataExtend

# 教學用: 最簡單版本, 只抓資料並印出, 不上傳資料庫
# 適合剛接觸 Celery 的人, 先確認「任務能被派送、worker 能收到、API 能呼叫」
# 之後再進階到 crawler_finmind (含資料庫寫入)
@app.task()
def crawler_finmind_print(stock_id):
    # FinMind API endpoint, 提供台股歷史股價等免費資料
    url = "https://api.finmindtrade.com/api/v4/data"
    # API 參數: 指定要抓哪個資料集、哪檔股票、日期範圍
    parameter = {
        "dataset": "TaiwanStockPrice",  # 台股日線資料
        "data_id": stock_id,  # 股票代碼, ex: 2330
        "start_date": "2024-01-01",
        "end_date": "2025-06-17",
    }
    # 發送 HTTP GET 請求, 把參數放在 query string
    resp = requests.get(url, params=parameter)
    # 將回傳的 JSON 轉成 Python dict
    data = resp.json()
    # HTTP 200 代表請求成功
    if resp.status_code == 200:
        # data["data"] 是 list of dict, 剛好可以直接轉成 DataFrame
        df = pd.DataFrame(data["data"])
        # 只印出資料, 不做後續處理
        print(df)
    else:
        # 若 API 失敗, 印出錯誤訊息方便排查
        print(data["msg"])

@app.task()
def crawler_tdx(title, sub_url, parameter):
    acess_token = get_tdx_token()
    
    url = "https://tdx.transportdata.tw/api/basic"
    id = "Kaohsiung"
    
    print(f"開始抓{title}站點資料")
    for i,j in enumerate(sub_url):
        data0 = get_tdx_title(url, j, parameter[i] ,token=acess_token)
        df = pd.DataFrame(data0)
        print(df)


def upload_data_to_mysql(df: pd.DataFrame, title):
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    # 上傳到 mydb, 同學可切換成自己的 database
    # 密碼要先 quote_plus 做 URL 編碼：連線字串裡 @ 分隔「帳密」與「主機」、: 分隔「主機」與「port」,
    # 密碼本身含這些符號時（強密碼常見）會把字串切歪, 出現 invalid literal for int() 之類的解析錯誤
    address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/mydb"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 多個 worker 同時首次寫入時，可能同時嘗試建表導致衝突
    # 第一次失敗後重試一次即可（表已被另一個 worker 建好）
    try:
        df.to_sql(
            f"{title}Table",
            con=engine,
            if_exists="append",
            index=False,
        )
        print(f"{title}Table建立Ok")
    except Exception:
        df.to_sql(
            f"{title}Table",
            con=engine,
            if_exists="append",
            index=False,
        )
        print(f"{title}Table建立Ok")


    
@app.task()
def crawler_mediaTW(url, page):
    #url = "https://media.taiwan.net.tw/zh-tw/portal/travel?DataCode=Trail&DataId=&Field=&Keyword=&County=&UpdateYearStart=&UpdateMonthStart=&UpdateYearEnd=&UpdateMonthEnd=&AttractionClass=&EventClass=&HotelClass=&CuisineClass=&TourismServiceSiteClass=&CyclingRouteClass=&TrailClass="

    response = requests.post(
                            url
                        )
    
    print("Access Token 取得成功")
    
    data0 = web_pageNext(url, page)
    print(data0)
    
    data_list = []
    
    for d in data0:
        url_page = f"https://media.taiwan.net.tw/zh-tw/portal/travel/details/{d.strip().lower()}"
        #print(url_page)
        headers = {
                    'User-Agent': (
                                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
                    )
        }
        response_item = requests.get(url_page, headers=headers)
        #print(response_item.raise_for_status())
                    
        soup_item = BeautifulSoup(response_item.text, 'html.parser')
        
        target = soup_item.find("a",class_='btn btn-block btn-maincolor my-3')
        url_d = f"https://media.taiwan.net.tw{target.get('href')}"

        # 2. 發送請求並直接解析 JSON
        try:
            response = requests.get(url_d, headers=headers)
            response.raise_for_status()

        # 將內容解析為 Python 的字典/列表
            data = response.json()
            print('資料獲取成功！這是一份 JSON 文字資料，而非 ZIP 檔。')

        # 3. 將資料儲存為 JSON 檔案（確保中文不會變成亂碼）
            output_file = 'data_d.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f'已成功將資料儲存至：{output_file}')

            with open('data_d.json', 'r', encoding='utf-8-sig') as f:
                d = json.load(f)
                data_list.append(d)
                #df = pd.json_normalize(d)

            #df =  pd.read_json('data_d.json')
            

        # # 4. 測試讀取並列印部分內容
        #     print('\n--- 步道資料預覽 ---')
        #     print(f"步道名稱：{data.get('TrailName')}")
        #     print(f"步道編號：{data.get('TrailID')}")
        #     print(f"步道簡介：{data.get('Description')[:50]}...")

        except requests.exceptions.HTTPError as e:
            print(f'連線失敗：{e}')
        except json.JSONDecodeError:
            print('伺服器回傳的內容不是標準的 JSON 格式！')
        except Exception as e:
            print(f'發生其他錯誤：{e}')
            
    df = pd.DataFrame(data_list)
    print(df)
    print(df.dtypes)

    df = dataExtend(data_list)

    upload_data_to_mysql(df,'attraction')














'''
        # 發送請求並直接解析 JSON
        try:
            response_item = requests.get(url_page, headers=headers)
            #print(response_item.raise_for_status())
            
            soup_item = BeautifulSoup(response_item.text, 'html.parser')

            target = soup_item.find("a",class_='btn btn-block btn-maincolor my-3')
            url_d = f"https://media.taiwan.net.tw{target.get('href')}"
            #print(url_d)
            
            res = requests.get(url_d)
            print(res)
            print(type(res))
            
            import os
            from urllib.parse import urlparse

            parsed_url = urlparse(url_d)
            filename = os.path.basename(parsed_url.path)

            # 如果網址結尾沒有檔名，就設定一個預設檔名
            if not filename:
                filename = "downloaded_file"

                response = requests.get(url_d)

            if  response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"下載完成，檔案儲存為：{filename}")
                with open(filename , 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                    df = pd.json_normalize(data)
                    print(df)
            
            else:
                print(f"下載失敗，錯誤代碼：{response.status_code}")
            

            # import json
            # import pandas as pd
            # with open(f'{filename}', 'r', encoding='utf-8-sig') as f:
            #     data = json.load(f)
            #     df = pd.json_normalize(data)
             
            #     print(df)
            
        finally:
            print('ok')
'''




'''
        # 將內容解析為 Python 的字典/列表
            data = response.json()
        #print('資料獲取成功！這是一份 JSON 文字資料，而非 ZIP 檔。')

        # 3. 將資料儲存為 JSON 檔案（確保中文不會變成亂碼）
            output_file = 'trail_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        print(f'已成功將步道資料儲存至：{output_file}')

        # 4. 測試讀取並列印部分內容
        print('\n--- 步道資料預覽 ---')
        print(f"步道名稱：{data.get('TrailName')}")
        print(f"步道編號：{data.get('TrailID')}")
        print(f"步道簡介：{data.get('Description')[:50]}...")

        except requests.exceptions.HTTPError as e:
        print(f'連線失敗：{e}')
        except json.JSONDecodeError:
        print('伺服器回傳的內容不是標準的 JSON 格式！')
        except Exception as e:
        print(f'發生其他錯誤：{e}')
'''





# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def crawler_finmind(stock_id):
    # FinMind API endpoint, 提供台股歷史股價等免費資料
    url = "https://api.finmindtrade.com/api/v4/data"
    # API 參數: 指定要抓哪個資料集、哪檔股票、日期範圍
    parameter = {
        "dataset": "TaiwanStockPrice",  # 台股日線資料
        "data_id": stock_id,  # 股票代碼, ex: 2330
        "start_date": "2024-01-01",
        "end_date": "2025-06-17",
    }
    # 發送 HTTP GET 請求, 把參數放在 query string
    resp = requests.get(url, params=parameter)
    # 將回傳的 JSON 轉成 Python dict
    data = resp.json()
    # HTTP 200 代表請求成功
    if resp.status_code == 200:
        # data["data"] 是 list of dict, 剛好可以直接轉成 DataFrame
        df = pd.DataFrame(data["data"])
        print(df)
        # print("upload db")
        # 雙寫: 同一份資料寫 MySQL（營運用）＋ BigQuery raw 層（分析用）
        upload_data_to_mysql(df)
        upload_data_to_bigquery_raw(df)
        # 手冊16 Spanner 體驗: 有設 SPANNER_INSTANCE 才會多寫一份
        upload_data_to_spanner_if_configured(df)
        # 同時存一份 CSV
        df.to_csv(f"output/TaiwanStockPrice_{stock_id}.csv", index=False, encoding="utf-8-sig")
        print(f"TaiwanStockPrice_{stock_id}.csv saved.")
    else:
        # 若 API 失敗, 印出錯誤訊息方便排查
        print(data["msg"])