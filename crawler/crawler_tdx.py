#載入官方套件
from tdx_proxy import TDXProxy
import requests

CLIENT_ID = "flykiller1220-522918b7-8d58-42d5"
CLIENT_SECRET = "8b67bb18-343d-40f3-a681-0980b1fc9b68"

def get_tdx_token(ID=CLIENT_ID,SECRET=CLIENT_SECRET):

# =========================
# 1. 取得 Access Token
# =========================

    token_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

    token_data = {
        "grant_type": "client_credentials",
        "client_id": ID,
        "client_secret": SECRET
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(
        token_url,
        data=token_data,
        headers=headers,
        timeout=30
    )


    print("Status Token Code:", token_response.raise_for_status())
    print("Access Token 取得成功")
    access_token = token_response.json()["access_token"]
    return access_token


# =========================
# 2. 呼叫TITLE API
# =========================

# api_url = (
#     "https://tdx.transportdata.tw/api/basic/v1/"
#     "Parking/OnStreet/ParkingSpot/City/Kaohsiung"
# )

api_main = "https://tdx.transportdata.tw/api/basic"
api_title = "/v1/Parking/OnStreet/ParkingSpot/City/"
api_parameter = "Kaohsiung"

def get_tdx_title(main=api_main,title=api_title,parameter=api_parameter,token=get_tdx_token()):

    api_url = f"{main}{title}{parameter}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    title_response = requests.get(
        api_url,
        headers=headers,
        timeout=30
    )

    
    print("Status Title Code:", title_response.raise_for_status())
    data0 = title_response.json()
    return data0
    #print(data0)
