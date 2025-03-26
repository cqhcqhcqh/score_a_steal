import requests
import time
import json
from src.tool.sign import calculate_sign
from src.model.build_user_info import build_seller_info

def goto_user_nav_page(cookies, headers, user_id):
    _m_h5_tk = cookies.get('_m_h5_tk')
    assert _m_h5_tk != None

    t = str(int(time.time() * 1000))
    api = 'mtop.idle.web.user.page.head'
    appKey = '34839810'
    spm_cnt = 'a21ybx.item.0.0'
    spm_pre = 'a21ybx.search.searchFeedList.1.25734829IcZ8UM'
    log_id = '25734829IcZ8UM'
    jsv = '2.7.2'
    v = '1.0'
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
    data_item = json.dumps({"self":False,"userId":user_id})
    
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
        f'https://h5api.m.goofish.com/h5/{api}/1.0/',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data,
    ).json()

    import os
    if not os.path.exists(f'sessions/{api}_.json'):
        with open(f'sessions/{api}_.json', 'w') as file:
            json.dump(responseJson, file, indent=2, ensure_ascii=False)
    if responseJson.get('ret') == ['SUCCESS::调用成功']:
        user_info = build_seller_info(responseJson['data'], user_id)
        if user_info.seller_id != user_id:
            raise Exception(f"mtop.idle.web.user.page.head 接口调用报错 user_id {user_id} not in responseJson['data']")
        return user_info
    else:
        raise Exception(f'{api} 接口调用报错 {responseJson.get('ret')}')