import time
import json
from src.tool.sign import calculate_sign

def test_goto_nav_page(user_id=None):
    import requests

    # cookies = {
    #     'cna': 'iDpoIFcW+kwCAXTjfPXE+L8v',
    #     'xlly_s': '1',
    #     'cookie2': '163500a5c58eff4e9581b5b98180baf9',
    #     '_samesite_flag_': 'true',
    #     't': '913e0e5e1851c3ef46e832963be33c96',
    #     '_tb_token_': '5ad13537368d7',
    #     'tracknick': 'tb817965751',
    #     'unb': '3921919291',
    #     'sgcookie': 'E100GoNO8j0H8LzH%2BO8w5Ej4kvOuYFWnoxgMKJbW%2B2Ast5II%2BY5XthuXGLYRoS4cTVohdcSWyq1D9LfMSuBLIdMB5H0Ya79TbZD8McP5CxaaXKrg%2FzXD7RyOZflfmvE13HGA',
    #     'csg': '9c31e70e',
    #     'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiYmYxOTFhYzM4ZDgzNWU4ZTlmMzYzZjUxNWI4MjI4YzgiLCJzaXRlIjo3NywidG9rZW4iOiIxa2hWUHkzWHo3OTRsMDdJM05vZG5TdyJ9',
    #     '_hvn_lgc_': '77',
    #     'havana_lgc_exp': '1745411335394',
    #     'sdkSilent': '1742905737730',
    #     'mtop_partitioned_detect': '1',
    #     '_m_h5_tk': '6399ca97ff3034fca1f02bce67ffb257_1742901939451',
    #     '_m_h5_tk_enc': 'b0d4f3160dbcd6e31369196b700dec1d',
    #     'x5sectag': '133623',
    #     'x5sec': '7b22733b32223a2266313262636336343738656661313333222c22617365727665723b33223a22307c434c627169623847454a58476c4d41474767777a4f5449784f5445354d6a6b784f7a497779656e4f7777633d227d',
    #     'isg': 'BEhIID2nu4lLfdcN73o-MQFvGbBa8az7VxS7WgL51EO23elHqgEmiwweVbWtbWTT',
    #     'tfstk': 'gfyEIigVpY4s6-yFrcDy_xdNDSHKUvbfz8gSquqoA20HdpTu_r4tR7NIR3ParPhI-YsKZ44g5MH7Uuprqu4Rv4sd1kEKeYbfl7WbvkpFruKLLpxMIlnyrpfst_ER1mbflt61thDP8ZaCMDiOQ03ix0co-Gkiv0HkZ44oSfmmceDoEzjZs0nkEQvotOqi0V0oEY4ujGoWrXr3qdojtgScmqTHhzhEok0w3leZx0RLAV8HRRPZTq4E7LvuQDr63mb2KtugO72IIJbMkAqY1ymZ3T-rbSriKDzRHpH3mlVoT85WD4FajSGa6HsKbJr4UmleSMu8dyyr9-bXB2VaB8kQ1wJjybV_pjeCSpk0MkMQZPjkE4PiqgWpyc2-Q8FerQlnXcufbGoCN4hC8QdfcQd-sxnZlMiBwQh3KcufjedJwXCtbqsHT',
    # }
    # cookies = {
    #     'cna': 'iDpoIFcW+kwCAXTjfPXE+L8v',
    #     'xlly_s': '1',
    #     'cookie2': '163500a5c58eff4e9581b5b98180baf9',
    #     '_samesite_flag_': 'true',
    #     't': '913e0e5e1851c3ef46e832963be33c96',
    #     '_tb_token_': '5ad13537368d7',
    #     'tracknick': 'tb817965751',
    #     'unb': '3921919291',
    #     'sgcookie': 'E100GoNO8j0H8LzH%2BO8w5Ej4kvOuYFWnoxgMKJbW%2B2Ast5II%2BY5XthuXGLYRoS4cTVohdcSWyq1D9LfMSuBLIdMB5H0Ya79TbZD8McP5CxaaXKrg%2FzXD7RyOZflfmvE13HGA',
    #     'csg': '9c31e70e',
    #     'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiYmYxOTFhYzM4ZDgzNWU4ZTlmMzYzZjUxNWI4MjI4YzgiLCJzaXRlIjo3NywidG9rZW4iOiIxa2hWUHkzWHo3OTRsMDdJM05vZG5TdyJ9',
    #     '_hvn_lgc_': '77',
    #     'havana_lgc_exp': '1745411335394',
    #     'sdkSilent': '1742905737730',
    #     'mtop_partitioned_detect': '1',
    #     '_m_h5_tk': '6399ca97ff3034fca1f02bce67ffb257_1742901939451',
    #     '_m_h5_tk_enc': 'b0d4f3160dbcd6e31369196b700dec1d',
    #     'isg': 'BEhIID2nu4lLfdcN73o-MQFvGbBa8az7VxS7WgL51EO23elHqgEmiwweVbWtbWTT',
    #     # 'tfstk': 'gfnIa1g8fbna0TfiKBpaCjYPY2rSPbt2VTw-nYIFekEdw_HY_XPUYLx7wXVZYWkUvYISFYVUzecPKVcqHMoe-uS7xuqJgI-20eD3qupCsMn8tAHgedyKl3ozBuqJgC7N2yxbqjvDThg-BdwzU8IKwyBT652V2uFLy1QTH5F82bULXNebF_eLeWI9C8VTwuIdJdZt1XBbFeNndpE9u2hRlgQQ6gI-fJa97vF9wVm_dvNxpDtMjqeQRSHL1Im4VLaSOyiwAs2IWxGgdbxcxkUSJqEKVItQXx0Z9RGJGaNtlDm7uDOfoWn3ZjZK5CIQ2lwjFruweZNZyAm_5DTVERmEeD44DnfLaVkjV8ikZhGjpXgYkDCC4Vs4GgfdPOacVRN2Cd_lrgMa0uVCWcpuJR2Q7d91944LIRZDCd_P9yegQ9p6CZ3F.',
    # }
    cookies = {
    'cna': 'iDpoIFcW+kwCAXTjfPXE+L8v',
    'xlly_s': '1',
    'cookie2': '163500a5c58eff4e9581b5b98180baf9',
    '_samesite_flag_': 'true',
    't': '913e0e5e1851c3ef46e832963be33c96',
    '_tb_token_': '5ad13537368d7',
    'tracknick': 'tb817965751',
    'unb': '3921919291',
    'sgcookie': 'E100GoNO8j0H8LzH%2BO8w5Ej4kvOuYFWnoxgMKJbW%2B2Ast5II%2BY5XthuXGLYRoS4cTVohdcSWyq1D9LfMSuBLIdMB5H0Ya79TbZD8McP5CxaaXKrg%2FzXD7RyOZflfmvE13HGA',
    'csg': '9c31e70e',
    'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiYmYxOTFhYzM4ZDgzNWU4ZTlmMzYzZjUxNWI4MjI4YzgiLCJzaXRlIjo3NywidG9rZW4iOiIxa2hWUHkzWHo3OTRsMDdJM05vZG5TdyJ9',
    '_hvn_lgc_': '77',
    'havana_lgc_exp': '1745411335394',
    'sdkSilent': '1742905737730',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': '6399ca97ff3034fca1f02bce67ffb257_1742901939451',
    '_m_h5_tk_enc': 'b0d4f3160dbcd6e31369196b700dec1d',
    'x5sectag': '927520',
    'x5sec': '7b22733b32223a2236653039653564313565663266363063222c22617365727665723b33223a22307c4349694969723847454f6d5a326148372f2f2f2f2f77456144444d354d6a45354d546b794f5445374d7a444a3663374442773d3d227d',
    'isg': 'BGBg2N06E0ESF69F1_KmadlnMWgyaUQzPwyjEtpxWnsO1QH_gnlIw-wmbX3V5fwL',
    # 'tfstk': 'gsnnQc_MN51XAScA9frBkGS6Qi8TA9Z7abI8wuFy75P196IKU_co_jHdv0HzZbcT173LyWhorbhZZz9Qw7PowYupBnKxdvZ74YAvDnC1Yy_tt_7UzLPaE8JTLqx-2Rr74IdOWgzBmuGXhm0rzAJge8ePYbyUQ1P_F9rzTz5N7-Paaulz85WaFJ7ULzrPbd27_7rzLgJgbfCF4SmrfcRNot9Ho8JIfJ43gvPEpvnwAy7IK5D-FcynIPHEdgSrjJ4nVecoY0rr8vhgk2AcxoHElbwqT6R3IDDmqqlwXMqoQqoubcRNBWujI0qKYLKUbDcnYPcP3wzElX34ScdhfSuZIYUi5L_LwqwrNriJGMNEUxijkoxlER0mQljrIN7qMrS7QLnNPaaUCRVxgSYNHhSKkmpMIZTQ8RwpMdvGPYzUCRfMIdbVWyy_Lz5..',
    }
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,tr;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.goofish.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.goofish.com/',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        # 'cookie': 'cna=iDpoIFcW+kwCAXTjfPXE+L8v; xlly_s=1; cookie2=163500a5c58eff4e9581b5b98180baf9; _samesite_flag_=true; t=913e0e5e1851c3ef46e832963be33c96; _tb_token_=5ad13537368d7; tracknick=tb817965751; unb=3921919291; sgcookie=E100GoNO8j0H8LzH%2BO8w5Ej4kvOuYFWnoxgMKJbW%2B2Ast5II%2BY5XthuXGLYRoS4cTVohdcSWyq1D9LfMSuBLIdMB5H0Ya79TbZD8McP5CxaaXKrg%2FzXD7RyOZflfmvE13HGA; csg=9c31e70e; havana_lgc2_77=eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiYmYxOTFhYzM4ZDgzNWU4ZTlmMzYzZjUxNWI4MjI4YzgiLCJzaXRlIjo3NywidG9rZW4iOiIxa2hWUHkzWHo3OTRsMDdJM05vZG5TdyJ9; _hvn_lgc_=77; havana_lgc_exp=1745411335394; sdkSilent=1742905737730; mtop_partitioned_detect=1; _m_h5_tk=6399ca97ff3034fca1f02bce67ffb257_1742901939451; _m_h5_tk_enc=b0d4f3160dbcd6e31369196b700dec1d; x5sectag=133623; x5sec=7b22733b32223a2266313262636336343738656661313333222c22617365727665723b33223a22307c434c627169623847454a58476c4d41474767777a4f5449784f5445354d6a6b784f7a497779656e4f7777633d227d; isg=BEhIID2nu4lLfdcN73o-MQFvGbBa8az7VxS7WgL51EO23elHqgEmiwweVbWtbWTT; tfstk=gfyEIigVpY4s6-yFrcDy_xdNDSHKUvbfz8gSquqoA20HdpTu_r4tR7NIR3ParPhI-YsKZ44g5MH7Uuprqu4Rv4sd1kEKeYbfl7WbvkpFruKLLpxMIlnyrpfst_ER1mbflt61thDP8ZaCMDiOQ03ix0co-Gkiv0HkZ44oSfmmceDoEzjZs0nkEQvotOqi0V0oEY4ujGoWrXr3qdojtgScmqTHhzhEok0w3leZx0RLAV8HRRPZTq4E7LvuQDr63mb2KtugO72IIJbMkAqY1ymZ3T-rbSriKDzRHpH3mlVoT85WD4FajSGa6HsKbJr4UmleSMu8dyyr9-bXB2VaB8kQ1wJjybV_pjeCSpk0MkMQZPjkE4PiqgWpyc2-Q8FerQlnXcufbGoCN4hC8QdfcQd-sxnZlMiBwQh3KcufjedJwXCtbqsHT',
    }
    
    params = {
        'jsv': '2.7.2',
        'appKey': '34839810',
        't': '1742894404834',
        'sign': '5c05d68ea778524791fb40acb0fab6ef',
        'v': '1.0',
        'type': 'originaljson',
        'accountSite': 'xianyu',
        'dataType': 'json',
        'timeout': '20000',
        'api': 'mtop.idle.web.user.page.head',
        'sessionOption': 'AutoLoginOnly',
        'spm_cnt': 'a21ybx.personal.0.0',
        'spm_pre': 'a21ybx.item.itemHeader.2.6f5d3da6A11msL',
        'log_id': '6f5d3da6A11msL',
    }
    
    data_item = json.dumps({"self":False,"userId":user_id})
    
    data = {
        'data': data_item,
    }

    t = str(int(time.time() * 1000))
    _m_h5_tk = cookies.get('_m_h5_tk')    
    token = _m_h5_tk.split('_')[0]
    sign = calculate_sign(token, t, params['appKey'], data_item)
    params['sign'] = sign
    params['t'] = t
    print('t:', params['t'])

    responseJson = requests.post(
        'https://h5api.m.goofish.com/h5/mtop.idle.web.user.page.head/1.0/',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data,
    ).json()
    if responseJson.get('ret') == ['FAIL_BIZ_USER_PAGE_FORBIDDEN::该用户因违反法规或闲鱼相关规则账号已被处置']:
        return None
    elif responseJson.get('ret') != ['SUCCESS::调用成功']:
        raise Exception(f'mtop.idle.web.user.page.head 接口调用报错 {responseJson.get('ret')}')
    else:
        return responseJson
    
import time

import sqlite3

# 连接数据库
conn = sqlite3.connect('search_results.db')
cursor = conn.cursor()

# 查询所有 seller_id
cursor.execute("SELECT seller_id FROM seller_info")
seller_ids = [row[0] for row in cursor.fetchall()]

# 关闭连接
cursor.close()
conn.close()

# print(seller_ids)  # 输出所有 seller_id 列表

for idx, seller_id in enumerate(seller_ids):
    print(f'test_goto_nav_page {idx} enter : {seller_id}')
    test_goto_nav_page(seller_id)
    time.sleep(1)
