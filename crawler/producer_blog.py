# 教學用版本: 使用 crawler_finmind_print (只抓取並印出, 不寫入資料庫)
# 適合初學者第一次派送任務時使用, 驗證 producer/worker 流程是否通暢
# 對應的 consumer 就是 tasks_crawler_finmind.py 裡註冊的 crawler_finmind_print task
from crawler.tasks_crawler_blog import crawler_blog


# for 迴圈, 可一次發送多個任務
# 這樣一次就能派送 5 支股票的爬蟲任務到 RabbitMQ
# Celery worker 會從 RabbitMQ 取出任務並平行處理, 比循序執行快很多

#TDX的各種參數
'''
TDX_title_lists = ['bus', 'train', 'metro', 'bike']
#TDX_title_lists = ['metro']
TDX_title_dicts = {'bus': ['/v2/Bus/Stop/City/', '/v2/Bus/Station/City/'], 
                   'train': ['/v3/Rail/TRA/Station'], 
                   'metro': ['/v2/Rail/Metro/Station/'], 
                   'bike': ['/v2/Bike/Station/City/']}
TDX_title_dicts2 = {'bus': ["Kaohsiung", "Kaohsiung"], 
                   'train': [""], 
                   'metro': ["KRTC"], 
                   'bike': ["Kaohsiung"]}
'''

# for stock_id in ["2330", "0050", "2317", "0056", "00713"]:
#     print(stock_id)
#     # .delay() 是 Celery 的非同步派送捷徑, 呼叫完會立刻回傳, 不等 task 執行完
#     crawler_finmind_print.delay(stock_id=stock_id)
    
#url_list = ['Attraction&DataId', 'Event&DataId', 'Restaurant&DataId', 'CyclingRoute&DataId', 'Trail&DataId']    
#url_list = ['Attraction&DataId']

url_list = [

]

crawler_pattern = [

]

#page_list = []

for index, url in enumerate(url_list):
    #print(f"預計抓{title}站點資料")
    # .delay() 是 Celery 的非同步派送捷徑, 呼叫完會立刻回傳, 不等 task 執行完
    crawler_blog.delay(url = url, pattern = crawler_pattern[index] , page = 100)