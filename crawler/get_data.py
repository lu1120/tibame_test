import pandas as pd
import json

def dataExtend(data0):
    # #print(data0.dtypes)
    # print(type(data0))
    # if type(data0) == list:
    #     print('確認data0為串列')

    #     data0_set = set()
    #     data0_list = []
    #     for value in data0:
    #         data0_list.append((value,type(value)))
    #         data0_set.add(type(value))

    #     if list in data0_set or dict in data0_set or object in data0_set:
            
    #         df0 = pd.DataFrame(data0)
            
    #         for i in data0_list:
    #             if i[1] == dict:
    #                 print(i[0])
    #                 print(type(i[0]))
    #                 extend_df = pd.json_normalize(df0.get(i[0]))
    #                 df0.drop(columns=[i[0]]).join(extend_df)
                               
    #         print(df0)
    #         return df0
    #     else:
    #         df0 = pd.DataFrame(data0)
    #         return df0

    # elif type(data0) == dict:
    #     print('確認data0為json')

    #     df0 = pd.DataFrame()
    #     data0_list = []
    #     data0_set = set()
    #     for key, value in data0.items():
    #         if type(value) == list :
    #             for i in value:
    #                 if type(i) == dict:
    #                     print(i)
    #                     expanded_df = pd.DataFrame(i)
    #                     print(expanded_df)
    #                 else:
    #                     pass
    #                 df0 = df0.join(expanded_df)
    #                 print(df0)
    #             data0.pop(key)
    #             print(12)
    #         else: 
    #             data0_list.append((key, value))
    #             data0_set.add(type(value))
    #             print(34)

    #     if list in data0_set or dict in data0_set or object in data0_set:
            
    #         #df0 = pd.DataFrame(data0)
    #         #df0 = pd.json_normalize(data0)
    #         df0_last = pd.json_normalize(data0)
    #         print(df0_last)
    #         #df0 = df0.join(df0_last)
    #         #df0 = pd.json_normalize(df0)
    #         # print(df0.dtypes)
    #         # for i in data0_list:
    #         #     if i[1] == dict:
    #         #         # print(i[0])
    #         #         # print(type(i[0]))
    #         #         # extend_df = pd.json_normalize(df0.get(i[0]))
    #         #         df0.drop(columns=[i[0]])
                    
    #         #print(type(df0))                               
    #         print(df0_last.T)
    #         #print(df0['Images'])
    #         #print(df0['SocialMediaURLs'])
    #         print(56)
    #         return df0_last    
    #     else:
    #         df0 = pd.DataFrame(data0)
    #         print(78)
    #         return df0

    # else:
    #     print('不屬於預想中的資料型態')
    #     print(type(data0))
    #     df0 = pd.DataFrame(data0)
    #     print(df0)
    #     print(df0.dtypes)
    #     return df0
        
        
        
  

    # 先用 json_normalize 處理基本巢狀（如 PostalAddress）
    df = pd.json_normalize(data0)

    # 找出所有依然是 list 或者是 dict 的欄位，將其轉換為 JSON 字串
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
            )

    print(df.T)
    return df