import requests
from sign import calculate_sign

cookies = {
    'cookie2': '11628b63f61c2559435d782fb1bce891',
    '_samesite_flag_': 'true',
    't': '520215afed8f84b888da6f6185b63b42',
    '_tb_token_': '506e73e31e635',
    'cna': 'a8ZbIOS6UkcCAd+n6+fCbHPi',
    'isg': 'BOLiUN_M8ekQ1-21eNf23uZ-M25EM-ZNVJ-f1Sx7d9UA_4N5FMN2XGo-LjsDTF7l',
    'tracknick': 'xy634504632719',
    'unb': '2215834458188',
    'havana_lgc2_77': 'eyJoaWQiOjIyMTU4MzQ0NTgxODgsInNnIjoiMmQ2NTk5MGZjYWFiMjk3ZjQyYWY5OGZhM2I0YjRiMmIiLCJzaXRlIjo3NywidG9rZW4iOiIxR2lQZmVZY2RlTnlOcXBzSzY0QThGdyJ9',
    '_hvn_lgc_': '77',
    'havana_lgc_exp': '1744638289419',
    'tfstk': 'g6OiCdYjMMZSC4x8XH5sevVNvZHdCP1fpnFADsIqLMSQXlF9uoxDY3LT6ILVmnxdA5ptCtI0o1OpBSItfsY22sm-2bhJ5F15g0nJDP6B4_7ubSrAQ6yFMZqBkdqk5F1bRyEqep8_mRBAEF5206WFkN543sSZ-X7OY574_ZrE-ZsFg5WV0erFzaqNus-282bfYi5VQUV88GK2fBoEaTMWCthiRHWG4FS3ZeOh7VjSNMN4oBf6-FLwLSP2tNXMGD5guP52QFKhedmus_YwFn_ybloccBYe_ZAjcXxDuU9VKIcg5gR9sLBWDqylcepkmTdtj7sNELpPKIG71FX5b6bBMDNNmpJ26O1bbmjXteRNoIijt3SydJyrz0Pf8qdUh-6NRwjJoRDJPjJaR5un-8J5Qw_Zw203hq6NRwxE-22rwO7C7UC..',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': '01f8509de8b49ff605586d1d12a7aba6_1742289393628',
    '_m_h5_tk_enc': '17093a40e0ba0e1c83debfa46bdce1cf',
    'sgcookie': 'E100G0ZJcjVK2lycbMFAnEFrcpQGqbFlEtRGe11%2F%2BloKRx76T2apfCxq6jFGPO6I3ewAoHbKJtQ%2FW5jc%2FLQQd0BRXuBvBiTh1bJLApjEbvE0oBk%3D',
    'csg': '593ce6e8',
    'sdkSilent': '1742365715435',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,tr;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.goofish.com',
    'priority': 'u=1, i',
    'referer': 'https://www.goofish.com/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    # 'cookie': 'cookie2=11628b63f61c2559435d782fb1bce891; _samesite_flag_=true; t=520215afed8f84b888da6f6185b63b42; _tb_token_=506e73e31e635; cna=a8ZbIOS6UkcCAd+n6+fCbHPi; isg=BOLiUN_M8ekQ1-21eNf23uZ-M25EM-ZNVJ-f1Sx7d9UA_4N5FMN2XGo-LjsDTF7l; tracknick=xy634504632719; unb=2215834458188; havana_lgc2_77=eyJoaWQiOjIyMTU4MzQ0NTgxODgsInNnIjoiMmQ2NTk5MGZjYWFiMjk3ZjQyYWY5OGZhM2I0YjRiMmIiLCJzaXRlIjo3NywidG9rZW4iOiIxR2lQZmVZY2RlTnlOcXBzSzY0QThGdyJ9; _hvn_lgc_=77; havana_lgc_exp=1744638289419; tfstk=g6OiCdYjMMZSC4x8XH5sevVNvZHdCP1fpnFADsIqLMSQXlF9uoxDY3LT6ILVmnxdA5ptCtI0o1OpBSItfsY22sm-2bhJ5F15g0nJDP6B4_7ubSrAQ6yFMZqBkdqk5F1bRyEqep8_mRBAEF5206WFkN543sSZ-X7OY574_ZrE-ZsFg5WV0erFzaqNus-282bfYi5VQUV88GK2fBoEaTMWCthiRHWG4FS3ZeOh7VjSNMN4oBf6-FLwLSP2tNXMGD5guP52QFKhedmus_YwFn_ybloccBYe_ZAjcXxDuU9VKIcg5gR9sLBWDqylcepkmTdtj7sNELpPKIG71FX5b6bBMDNNmpJ26O1bbmjXteRNoIijt3SydJyrz0Pf8qdUh-6NRwjJoRDJPjJaR5un-8J5Qw_Zw203hq6NRwxE-22rwO7C7UC..; mtop_partitioned_detect=1; _m_h5_tk=01f8509de8b49ff605586d1d12a7aba6_1742289393628; _m_h5_tk_enc=17093a40e0ba0e1c83debfa46bdce1cf; sgcookie=E100G0ZJcjVK2lycbMFAnEFrcpQGqbFlEtRGe11%2F%2BloKRx76T2apfCxq6jFGPO6I3ewAoHbKJtQ%2FW5jc%2FLQQd0BRXuBvBiTh1bJLApjEbvE0oBk%3D; csg=593ce6e8; sdkSilent=1742365715435',
}

import time
t = str(int(time.time() * 1000))
params = {
    'jsv': '2.7.2',
    'appKey': '34839810',
    't': t,
    # 'sign': 'bad2b90b6b472c0ae5168e5d1bce5e00',
    'v': '1.0',
    'type': 'originaljson',
    'accountSite': 'xianyu',
    'dataType': 'json',
    'timeout': '20000',
    'api': 'mtop.taobao.idlemtopsearch.pc.search',
    'sessionOption': 'AutoLoginOnly',
    # 'spm_cnt': 'a21ybx.search.0.0',
    # 'spm_pre': 'a21ybx.search.searchInput.0',
}

data = {
    'data': '{"pageNumber":1,"keyword":"Phone14pro","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}',
}

sign = calculate_sign(token=cookies.get('_m_h5_tk').split('_')[0], t=params.get('t'), appKey=params.get('appKey'), data=data.get('data'))
params['sign'] = sign

response = requests.post(
    'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
    verify=False,
)

print(response.text)