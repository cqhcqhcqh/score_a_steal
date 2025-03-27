import requests

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
    'sdkSilent': '1743044436640',
    'sgcookie': 'E1001lElcOwgYlhuq2WPXASSttNjXCMEkO69I62AkN2zTVfDb%2BQByjv2fhfXyeBotC2vd0huaHP%2FPksrr8oDcayRDMDcz%2FaeHASeB1pCa8R1fwtqVa9t9%2FqiGSTQv7SNfx4F',
    'csg': 'db969cc4',
    'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiY2ExYjhhYjZmZDhhZGE2YjU1M2Y3MTkwNDI3ZmZkMTIiLCJzaXRlIjo3NywidG9rZW4iOiIxeHlralFRZkFfemNWUVItNEpkRVhaUSJ9',
    '_hvn_lgc_': '77',
    'havana_lgc_exp': '1745554849156',
    'tfstk': 'guwxwbsTygKxGnHhnt1kIkjy1BslKRE4irrBIV0D1zU8Ak8m1-D0WCU0bPc1ux2Tylad0cb4InPz-k90nskMBxkZCwbhK9f40Ak_06YQqqr74csocLPG3GDZCwblK9q40AzUK_t_1us-jcm6GPijF4grXIO_5qGWPDnECVa_54MSjDus5m9bVTgrfA9b5As-FfTFW4tjSdFCw9pAsCtYMuy-Dj3Q26JwIuvnM2wqyd_QemUsRogJCdgDGWQ7fP_9IvNUyRhQ-OprnkFSFmFRfQgj9Sam4PBphqw8c-g0havml-r7tR45fdgTNWG_Oo_kw0F7m8hudwptg7a4TfeGr9k0tk2ZO-6v84cEXyHbwa9YRg-UKJFOFe0KjIsR2CRZG08Q89ba8pqaa03hDOdw_bSr22j-zCRZi2i--g26_Cl-h',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': 'd83c8e1a7d8ae1cfc893725f82a6b01a_1743053622677',
    '_m_h5_tk_enc': '82ee876b9f6e05ce6f7212dcd6468f60',
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
    # 'cookie': 'cna=iDpoIFcW+kwCAXTjfPXE+L8v; xlly_s=1; cookie2=163500a5c58eff4e9581b5b98180baf9; _samesite_flag_=true; t=913e0e5e1851c3ef46e832963be33c96; _tb_token_=5ad13537368d7; tracknick=tb817965751; unb=3921919291; isg=BGBg2N06E0ESF69F1_KmadlnMWgyaUQzPwyjEtpxWnsO1QH_gnlIw-wmbX3V5fwL; sdkSilent=1743044436640; sgcookie=E1001lElcOwgYlhuq2WPXASSttNjXCMEkO69I62AkN2zTVfDb%2BQByjv2fhfXyeBotC2vd0huaHP%2FPksrr8oDcayRDMDcz%2FaeHASeB1pCa8R1fwtqVa9t9%2FqiGSTQv7SNfx4F; csg=db969cc4; havana_lgc2_77=eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiY2ExYjhhYjZmZDhhZGE2YjU1M2Y3MTkwNDI3ZmZkMTIiLCJzaXRlIjo3NywidG9rZW4iOiIxeHlralFRZkFfemNWUVItNEpkRVhaUSJ9; _hvn_lgc_=77; havana_lgc_exp=1745554849156; tfstk=guwxwbsTygKxGnHhnt1kIkjy1BslKRE4irrBIV0D1zU8Ak8m1-D0WCU0bPc1ux2Tylad0cb4InPz-k90nskMBxkZCwbhK9f40Ak_06YQqqr74csocLPG3GDZCwblK9q40AzUK_t_1us-jcm6GPijF4grXIO_5qGWPDnECVa_54MSjDus5m9bVTgrfA9b5As-FfTFW4tjSdFCw9pAsCtYMuy-Dj3Q26JwIuvnM2wqyd_QemUsRogJCdgDGWQ7fP_9IvNUyRhQ-OprnkFSFmFRfQgj9Sam4PBphqw8c-g0havml-r7tR45fdgTNWG_Oo_kw0F7m8hudwptg7a4TfeGr9k0tk2ZO-6v84cEXyHbwa9YRg-UKJFOFe0KjIsR2CRZG08Q89ba8pqaa03hDOdw_bSr22j-zCRZi2i--g26_Cl-h; mtop_partitioned_detect=1; _m_h5_tk=d83c8e1a7d8ae1cfc893725f82a6b01a_1743053622677; _m_h5_tk_enc=82ee876b9f6e05ce6f7212dcd6468f60',
}

params = {
    'jsv': '2.7.2',
    'appKey': '34839810',
    't': '1743043905682',
    'sign': '123c49436205b9b09b97a02824df0a27',
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
    'data': '{"pageNumber":1,"keyword":"苹果14pro","fromFilter":true,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{"searchFilter":"quickFilter:filterPersonal;"},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}',
}

response = requests.post(
    'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)