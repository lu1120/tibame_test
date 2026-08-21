#載入官方套件
#from tdx_proxy import TDXProxy
import requests
from crawler_tdx import get_tdx_token, get_tdx_title

#用套件函式取的token
get_tdx_token()


#用套件函式取的title data
get_tdx_title()

#title data處理 先print 後db

