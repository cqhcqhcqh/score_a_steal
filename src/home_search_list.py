import requests

# cookies = {
#     'mtop_partitioned_detect': '1',
#     'havana_lgc_exp': '1745019190281',
#     '_hvn_lgc_': '77',
#     'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiOTRjMWQ2ZjY5NTIxMGY1N2QyZmI0MzE5NTZhNmY1ZWMiLCJzaXRlIjo3NywidG9rZW4iOiIxeDVWVmloaWJaZ3NSU3M5QVlZWkhMZyJ9',
#     '_tb_token_': '55b1ea7333be3',
#     'xlly_s': '1',
#     'tracknick': 'tb817965751',
#     '_samesite_flag_': 'true',
#     't': '1bae4f773ac3d86e04a1603545be3dc8',
#     'unb': '3921919291',
#     'cna': 'rDpgIKd3eC8CAd+n6+dApg1s',
#     'sdkSilent': '1742513644409',
#     'mtop_partitioned_detect': '1',
#     '_m_h5_tk': '0205fb81c63e4e357d47003aa2fdc9ce_1742434870100',
#     '_m_h5_tk_enc': '2e8fef823d531d8aee27ad75079801fe',
#     'cookie2': '25a679a2b59f7fb3f4e3cb94414f3a96',
#     'sgcookie': 'E100Y4V17ETmhzfdAl0KSB3FBYcE39eT%2Bh4KBTZjTorJUBGeePhrRfbLgXEeK%2BI%2FORneQqoLNUOP2DBQzEh4DWakNbvUka3Fd0TgQUteKydulRgvNO2EQBOiUwR9mPWX%2FEgQ',
#     'csg': 'e0c79423',
#     'tfstk': 'g8RxBjcge4UYTI1nijMuseNqt20kBCL2nn8QsGj0C3KJRercCIfDXRKD7hXs0sA92FtKuNm2srJyxeNDix5g6s5N1DmntXb2u156qPTFWoS5RwlGl5_fg_wBmEhKtXY2lrbj-UGHiDqkrij11t61F7sPW5s6ftwWPg7N5o__G4L54g_bGS61N__CSRaXf1gJPg711ZTrcYIahMV9dzUtUM0apJwBwZBAX5jz66d4tTIQqgPT6nqRhMGh25N6wZTuzgb_GXIWndOcNIi7A_TeEn_R9jEFkLTp29Auq5fBL3dOdHgg3axv0I7eeDFViepWiTRIqS-9-ndOKncSlh5f5hWesDPVcFTeTpfKMk7vFeKRKQquTg79tBCyPkjdS-g-yRyNhaztZr9WkX_iWaInrZ2aQTHPyM0-ARw_YGQRx42LQRWrl',
# }

import time
import json
import requests
from .sign import calculate_sign

def get_home_search_result(cookies, headers, keyword, pageNumber=1):
    _m_h5_tk = cookies.get('_m_h5_tk')
    assert _m_h5_tk != None

    t = str(int(time.time() * 1000))
    api = 'mtop.taobao.idlemtopsearch.pc.search'
    appKey = '34839810'
    spm_cnt = 'a21ybx.item.0.0'
    spm_pre = 'a21ybx.search.searchFeedList.1.25734829IcZ8UM'
    log_id = '25734829IcZ8UM'
    jsv = '2.7.2'
    v = '1.0'
    rowsPerPage = 30
    # jsv=2.7.2&appKey=34839810&t=1742290911572&sign=1a7f1abda4bdf9ce025c8a1e89d971b2&v=1.0&type=originaljson&accountSite=xianyu&dataType=json&timeout=20000&api=mtop.taobao.idlemtopsearch.pc.search&sessionOption=AutoLoginOnly&spm_cnt=a21ybx.search.0.0&spm_pre=a21ybx.home.searchInput.0
    params = {
        'jsv': jsv,
        'appKey': appKey,
        't': t,
        # 'sign': '256a8f3bae5b7118e4dd60b715a97238',
        'v': v,
        'type': 'originaljson',
        'accountSite': 'xianyu',
        'dataType': 'json',
        'timeout': '20000',
        'api': api,
        'sessionOption': 'AutoLoginOnly',
        # 'spm_cnt': spm_cnt,
        # 'spm_pre': spm_pre,
        # 'log_id': log_id,
    }
    # "sortValue":"asc", # 按照价格升序
    # "sortField":"price", # 按照价格排序
    data_item = json.dumps(
                {"pageNumber":pageNumber,
                 "keyword": keyword,
                 "fromFilter":True,
                 "rowsPerPage":rowsPerPage,
                 "sortValue":"desc",
                 "sortField":"create", # 按照发布日期排序
                 "customDistance":"",
                 "gps":"",
                 "propValueStr":{"searchFilter":"quickFilter:filterPersonal;"}, # 个人闲置
                 "customGps":"",
                 "searchReqFromPage":"pcSearch",
                 "extraFilterValue":"{}",
                 "userPositionJson":"{}"})
    
    data = {
        'data': data_item,
    }

    token = _m_h5_tk.split('_')[0]
    sign = calculate_sign(token, t, appKey, data_item)
    params['sign'] = sign
    # cookies = {
    #     'cookie2': '11628b63f61c2559435d782fb1bce891',
    #     '_samesite_flag_': 'true',
    #     't': '520215afed8f84b888da6f6185b63b42',
    #     '_tb_token_': '506e73e31e635',
    #     'cna': 'a8ZbIOS6UkcCAd+n6+fCbHPi',
    #     'isg': 'BOLiUN_M8ekQ1-21eNf23uZ-M25EM-ZNVJ-f1Sx7d9UA_4N5FMN2XGo-LjsDTF7l',
    #     'tracknick': 'xy634504632719',
    #     'unb': '2215834458188',
    #     'havana_lgc2_77': 'eyJoaWQiOjIyMTU4MzQ0NTgxODgsInNnIjoiMmQ2NTk5MGZjYWFiMjk3ZjQyYWY5OGZhM2I0YjRiMmIiLCJzaXRlIjo3NywidG9rZW4iOiIxR2lQZmVZY2RlTnlOcXBzSzY0QThGdyJ9',
    #     '_hvn_lgc_': '77',
    #     'havana_lgc_exp': '1744638289419',
    #     'mtop_partitioned_detect': '1',
    #     '_m_h5_tk': '01f8509de8b49ff605586d1d12a7aba6_1742289393628',
    #     '_m_h5_tk_enc': '17093a40e0ba0e1c83debfa46bdce1cf',
    #     'sgcookie': 'E100G0ZJcjVK2lycbMFAnEFrcpQGqbFlEtRGe11%2F%2BloKRx76T2apfCxq6jFGPO6I3ewAoHbKJtQ%2FW5jc%2FLQQd0BRXuBvBiTh1bJLApjEbvE0oBk%3D',
    #     'csg': '593ce6e8',
    #     'sdkSilent': '1742365715435',
    #     'tfstk': 'gSrI_-1yC7EabqOgK6BZClnphQo5g7s2FLM8n8KeeDnpwQex_WlEYTjSwWcaYXyEvbK7a8rUauwkVYe8Z9cPKNy3K0mRgs5V0J23r991R1oReRnrFC2zRIw3K0vGgsSV0JAW84J1N0F-XVHrE0L-yHB1XxG9vYKKeCBsEfn-w7nRCRhie0Hpol-IQ9Ggd9FcoITKbjeK13KWnvgKMic623EsdIlYdqxJ2lMIRuftALpK2yeU1qzCGHibprVoHWddNbq_BkH7q_j_N8e0yVZ5ApcYYkaqo7WJlb2al7g4Y6tm9qa4kVZlmH2IoXnsIu5MvbaTykunqBCSZlwTvYZlZGNA4vtqG4sePdgDVAGVCOTkrEQ0pglb4qtSJADNaO66u80KIAZVCOTl12HiQ4X1CE5l.',
    #     'xlly_s': '1',
    # }

    # headers = {
    #     'accept': 'application/json',
    #     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,tr;q=0.7',
    #     'cache-control': 'no-cache',
    #     'content-type': 'application/x-www-form-urlencoded',
    #     'origin': 'https://www.goofish.com',
    #     'pragma': 'no-cache',
    #     'priority': 'u=1, i',
    #     'referer': 'https://www.goofish.com/',
    #     'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"macOS"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-site',
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    #     # 'cookie': 'cookie2=11628b63f61c2559435d782fb1bce891; _samesite_flag_=true; t=520215afed8f84b888da6f6185b63b42; _tb_token_=506e73e31e635; cna=a8ZbIOS6UkcCAd+n6+fCbHPi; isg=BOLiUN_M8ekQ1-21eNf23uZ-M25EM-ZNVJ-f1Sx7d9UA_4N5FMN2XGo-LjsDTF7l; tracknick=xy634504632719; unb=2215834458188; havana_lgc2_77=eyJoaWQiOjIyMTU4MzQ0NTgxODgsInNnIjoiMmQ2NTk5MGZjYWFiMjk3ZjQyYWY5OGZhM2I0YjRiMmIiLCJzaXRlIjo3NywidG9rZW4iOiIxR2lQZmVZY2RlTnlOcXBzSzY0QThGdyJ9; _hvn_lgc_=77; havana_lgc_exp=1744638289419; mtop_partitioned_detect=1; _m_h5_tk=01f8509de8b49ff605586d1d12a7aba6_1742289393628; _m_h5_tk_enc=17093a40e0ba0e1c83debfa46bdce1cf; sgcookie=E100G0ZJcjVK2lycbMFAnEFrcpQGqbFlEtRGe11%2F%2BloKRx76T2apfCxq6jFGPO6I3ewAoHbKJtQ%2FW5jc%2FLQQd0BRXuBvBiTh1bJLApjEbvE0oBk%3D; csg=593ce6e8; sdkSilent=1742365715435; tfstk=gSrI_-1yC7EabqOgK6BZClnphQo5g7s2FLM8n8KeeDnpwQex_WlEYTjSwWcaYXyEvbK7a8rUauwkVYe8Z9cPKNy3K0mRgs5V0J23r991R1oReRnrFC2zRIw3K0vGgsSV0JAW84J1N0F-XVHrE0L-yHB1XxG9vYKKeCBsEfn-w7nRCRhie0Hpol-IQ9Ggd9FcoITKbjeK13KWnvgKMic623EsdIlYdqxJ2lMIRuftALpK2yeU1qzCGHibprVoHWddNbq_BkH7q_j_N8e0yVZ5ApcYYkaqo7WJlb2al7g4Y6tm9qa4kVZlmH2IoXnsIu5MvbaTykunqBCSZlwTvYZlZGNA4vtqG4sePdgDVAGVCOTkrEQ0pglb4qtSJADNaO66u80KIAZVCOTl12HiQ4X1CE5l.; xlly_s=1',
    # }

    # params = {
    #     'jsv': '2.7.2',
    #     'appKey': '34839810',
    #     # 't': '1742280255254',
    #     # 'sign': '256a8f3bae5b7118e4dd60b715a97238',
    #     'v': '1.0',
    #     'type': 'originaljson',
    #     'accountSite': 'xianyu',
    #     'dataType': 'json',
    #     'timeout': '20000',
    #     'api': 'mtop.taobao.idle.pc.detail',
    #     'sessionOption': 'AutoLoginOnly',
    #     'spm_cnt': 'a21ybx.item.0.0',
    #     'spm_pre': 'a21ybx.search.searchFeedList.1.25734829IcZ8UM',
    #     'log_id': '25734829IcZ8UM',
    # }

    # data = {
    #     'data': '{"itemId":"897358282666"}',
    # }

    responseJson = requests.post(
        'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data,
    ).json()

    import os
    if not os.path.exists('sessions/mtop.taobao.idlemtopsearch.pc.search_.json'):
        with open('sessions/mtop.taobao.idlemtopsearch.pc.search_.json', 'w') as file:
            json.dump(responseJson, file, indent=2, ensure_ascii=False)
    resultList = responseJson.get('data').get('resultList')
    hasMore = len(resultList) == rowsPerPage
    return resultList, hasMore