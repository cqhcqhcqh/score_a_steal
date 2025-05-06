import json
import requests
from src.logger.app_logger import app_logger as logger

def get_home_list():
    cookies = {
        'cna': 'iDpoIFcW+kwCAXTjfPXE+L8v',
        'xlly_s': '1',
        'cookie2': '163500a5c58eff4e9581b5b98180baf9',
        '_samesite_flag_': 'true',
        't': '913e0e5e1851c3ef46e832963be33c96',
        '_tb_token_': '5ad13537368d7',
        'tracknick': 'tb817965751',
        'unb': '3921919291',
        'isg': 'BGBg2N06E0ESF69F1_KmadlnMWgyaUQzPwyjEtpxWnsO1QH_gnlIw-wmbX3V5fwL',
        'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiY2ExYjhhYjZmZDhhZGE2YjU1M2Y3MTkwNDI3ZmZkMTIiLCJzaXRlIjo3NywidG9rZW4iOiIxeHlralFRZkFfemNWUVItNEpkRVhaUSJ9',
        '_hvn_lgc_': '77',
        'havana_lgc_exp': '1745554849156',
        'mtop_partitioned_detect': '1',
        '_m_h5_tk': 'fb8083fec734c641912e5fb5d6cdef6e_1743065680619',
        '_m_h5_tk_enc': 'c851df2413f601e5770faee62d5886af',
        'sgcookie': 'E1005trk9MUQYtcLwwvZNgl%2Fye19uIdyrT0%2F91qZZ3hcNahRLRRjADzsBFW8IK5t2PlVPhfx9OWmIlL1kSOl1OL7f0kbvdEdavDeluhqAZCDA0%2BduMB24GzMovdCaCqGElYW',
        'csg': '20ad32da',
        'sdkSilent': '1743141642538',
        'tfstk': 'gvZZCDcPXmVBwXZNivm28UnDXvmt0cf5uoGjn-2mCfcMfhO087VK1ras1KzUiW3ssf6t0qV0sSuABjGmgSw059s5VRetDm2VNgs5VoTs-5-inqXmxxMVdAxLlGBjDmf5OetmWgoYwuwBzP2hLxMjnnVmSvAn9x-miSci-BDremc0iSmhxYkWmjYMSMXEHXcmmmVmxUP4I-xEFVXVO27RMpFm7b2iT3yLYAAxaghpmtEnQJlTIrKDmkkZ7oQaglqmmP2_T4aNaho7IzFxE5AG_vraUozutMtZ0J4u0DqhtpGgyJrqflXfjDqa_l0UiLYiSzF_r2rC_Hhu-Jyj8yBv5ja-nS38c_Kts-282ziP0KkUzJmF4fdxKonUDPRDuVDKLb6FLA_jMV1wkU6WkE3n2vl5CATvkVVxLb6EeELxWnkENOjd.',
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,tr;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.goofish.com',
        'priority': 'u=1, i',
        'referer': 'https://www.goofish.com/',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        # 'cookie': 'cna=iDpoIFcW+kwCAXTjfPXE+L8v; xlly_s=1; cookie2=163500a5c58eff4e9581b5b98180baf9; _samesite_flag_=true; t=913e0e5e1851c3ef46e832963be33c96; _tb_token_=5ad13537368d7; tracknick=tb817965751; unb=3921919291; isg=BGBg2N06E0ESF69F1_KmadlnMWgyaUQzPwyjEtpxWnsO1QH_gnlIw-wmbX3V5fwL; havana_lgc2_77=eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiY2ExYjhhYjZmZDhhZGE2YjU1M2Y3MTkwNDI3ZmZkMTIiLCJzaXRlIjo3NywidG9rZW4iOiIxeHlralFRZkFfemNWUVItNEpkRVhaUSJ9; _hvn_lgc_=77; havana_lgc_exp=1745554849156; mtop_partitioned_detect=1; _m_h5_tk=fb8083fec734c641912e5fb5d6cdef6e_1743065680619; _m_h5_tk_enc=c851df2413f601e5770faee62d5886af; sgcookie=E1005trk9MUQYtcLwwvZNgl%2Fye19uIdyrT0%2F91qZZ3hcNahRLRRjADzsBFW8IK5t2PlVPhfx9OWmIlL1kSOl1OL7f0kbvdEdavDeluhqAZCDA0%2BduMB24GzMovdCaCqGElYW; csg=20ad32da; sdkSilent=1743141642538; tfstk=gvZZCDcPXmVBwXZNivm28UnDXvmt0cf5uoGjn-2mCfcMfhO087VK1ras1KzUiW3ssf6t0qV0sSuABjGmgSw059s5VRetDm2VNgs5VoTs-5-inqXmxxMVdAxLlGBjDmf5OetmWgoYwuwBzP2hLxMjnnVmSvAn9x-miSci-BDremc0iSmhxYkWmjYMSMXEHXcmmmVmxUP4I-xEFVXVO27RMpFm7b2iT3yLYAAxaghpmtEnQJlTIrKDmkkZ7oQaglqmmP2_T4aNaho7IzFxE5AG_vraUozutMtZ0J4u0DqhtpGgyJrqflXfjDqa_l0UiLYiSzF_r2rC_Hhu-Jyj8yBv5ja-nS38c_Kts-282ziP0KkUzJmF4fdxKonUDPRDuVDKLb6FLA_jMV1wkU6WkE3n2vl5CATvkVVxLb6EeELxWnkENOjd.',
    }

    params = {
        'jsv': '2.7.2',
        'appKey': '34839810',
        't': '1743055258594',
        'sign': 'a22a28ce30267dc0b3c472b3c50dde04',
        'v': '1.0',
        'type': 'originaljson',
        'accountSite': 'xianyu',
        'dataType': 'json',
        'timeout': '20000',
        'api': 'mtop.taobao.idlemtopsearch.pc.search',
        'sessionOption': 'AutoLoginOnly',
        'spm_cnt': 'a21ybx.search.0.0',
        'spm_pre': 'a21ybx.search.searchInput.0',
    }

    data = {
        'data': '{"pageNumber":1,"keyword":"苹果16pro","fromFilter":true,"rowsPerPage":30,"sortValue":"desc","sortField":"create","customDistance":"","gps":"","propValueStr":{"searchFilter":"quickFilter:filterPersonal;"},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}',
    }

    with open('./test/test_home_list_filter.json', 'w+') as f:
        # headers = {key: value for key, value in headers._headers} if hasattr(headers, '_headers') else headers
        json.dump({'cookies': cookies,
                   'headers': headers, 
                   'data': data, 
                   'params': params}, 
                   f, 
                   indent=2, 
                   ensure_ascii=False)
        
    response = requests.post(
        'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/',
        params=params,
        cookies=cookies,
        headers=headers,
        data=data,
    )
    logger.info(f'reponseJson ret: {response.json().get('ret')}')

if __name__ == '__main__':
    get_home_list()