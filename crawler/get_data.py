import pandas as pd

def dataExtend(data0):
    #print(data0.dtypes)
    print(type(data0))
    if type(data0) == list:
        print('確認data0為串列')

        data0_set = set()
        data0_list = []
        for index , value in enumerate(data0):
            data0_list.append(index,type(value))
            data0_set.add(type(value))

        if list in data0_set or dict in data0_set or object in data0_set:

            df0 = pd.json_normalize(data0)
            print(df0)
            print(type(df0))
            print(df0.dtypes)
            return df0
        else:
            pass

    elif type(data0) == dict:
        print('確認data0為json')

        data0_list = set()
        for value in data0.values():
            data0_list.add(type(value))

        if list in data0_list or dict in data0_list or object in data0_list:

            df0 = pd.json_normalize(data0)
            print(df0)
            print(df0.dtypes)
            return df0
        else:
            pass

    else:
        print('不屬於預想中的資料型態')
        print(type(data0))
        df0 = pd.DataFrame(data0)
        print(df0)
        print(df0.dtypes)
        return df0
        