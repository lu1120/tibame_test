from urllib.parse import quote_plus  # 密碼含 @ : % 等符號時要先做 URL 編碼才能進連線字串

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
from crawler.worker import app
from crawler.crawler_tdx import get_tdx_token, get_tdx_title
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
        
        #print(type(df))
        #print(type(title))
        print(df.columns)
        print(df.dtypes)
        #df = df['UpdateTime']
        #df = pd.json_normalize(df.get('StopPosition'))
        # 假設 df['dict_col'] 裡面是字典
        #print(df['StationName'])
        #print(df['StationPosition'])
        # expanded_df = pd.json_normalize(df.get('StationName'))
        # expanded_df2 = pd.json_normalize(df.get('StationPosition'))

        # # 將展開後的結果與原本的 df 合併，並移除舊的字典欄位
        # #df = df.drop(columns=['StopName']).join(expanded_df)
        # #df = df.drop(columns=['StopPosition']).join(expanded_df2)
        # df = df.drop(columns=['StationName']).join(expanded_df)
        # df = df.drop(columns=['StationPosition']).join(expanded_df2)
        # print(df.dtypes)

        dataExtend(data0)

        #upload_data_to_mysql(df,title)


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