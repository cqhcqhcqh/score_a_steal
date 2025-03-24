import requests
from .sign import calculate_sign

cookies = {
    'mtop_partitioned_detect': '1',
    'havana_lgc_exp': '1745019190281',
    '_hvn_lgc_': '77',
    'havana_lgc2_77': 'eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiOTRjMWQ2ZjY5NTIxMGY1N2QyZmI0MzE5NTZhNmY1ZWMiLCJzaXRlIjo3NywidG9rZW4iOiIxeDVWVmloaWJaZ3NSU3M5QVlZWkhMZyJ9',
    '_tb_token_': '55b1ea7333be3',
    'xlly_s': '1',
    'tracknick': 'tb817965751',
    '_samesite_flag_': 'true',
    't': '1bae4f773ac3d86e04a1603545be3dc8',
    'unb': '3921919291',
    'cna': 'rDpgIKd3eC8CAd+n6+dApg1s',
    'sdkSilent': '1742513644409',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': '0205fb81c63e4e357d47003aa2fdc9ce_1742434870100',
    '_m_h5_tk_enc': '2e8fef823d531d8aee27ad75079801fe',
    'cookie2': '25a679a2b59f7fb3f4e3cb94414f3a96',
    'sgcookie': 'E100Y4V17ETmhzfdAl0KSB3FBYcE39eT%2Bh4KBTZjTorJUBGeePhrRfbLgXEeK%2BI%2FORneQqoLNUOP2DBQzEh4DWakNbvUka3Fd0TgQUteKydulRgvNO2EQBOiUwR9mPWX%2FEgQ',
    'csg': 'e0c79423',
    'tfstk': 'g8RxBjcge4UYTI1nijMuseNqt20kBCL2nn8QsGj0C3KJRercCIfDXRKD7hXs0sA92FtKuNm2srJyxeNDix5g6s5N1DmntXb2u156qPTFWoS5RwlGl5_fg_wBmEhKtXY2lrbj-UGHiDqkrij11t61F7sPW5s6ftwWPg7N5o__G4L54g_bGS61N__CSRaXf1gJPg711ZTrcYIahMV9dzUtUM0apJwBwZBAX5jz66d4tTIQqgPT6nqRhMGh25N6wZTuzgb_GXIWndOcNIi7A_TeEn_R9jEFkLTp29Auq5fBL3dOdHgg3axv0I7eeDFViepWiTRIqS-9-ndOKncSlh5f5hWesDPVcFTeTpfKMk7vFeKRKQquTg79tBCyPkjdS-g-yRyNhaztZr9WkX_iWaInrZ2aQTHPyM0-ARw_YGQRx42LQRWrl',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
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
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    # 'cookie': 'mtop_partitioned_detect=1; havana_lgc_exp=1745019190281; _hvn_lgc_=77; havana_lgc2_77=eyJoaWQiOjM5MjE5MTkyOTEsInNnIjoiOTRjMWQ2ZjY5NTIxMGY1N2QyZmI0MzE5NTZhNmY1ZWMiLCJzaXRlIjo3NywidG9rZW4iOiIxeDVWVmloaWJaZ3NSU3M5QVlZWkhMZyJ9; _tb_token_=55b1ea7333be3; xlly_s=1; tracknick=tb817965751; _samesite_flag_=true; t=1bae4f773ac3d86e04a1603545be3dc8; unb=3921919291; cna=rDpgIKd3eC8CAd+n6+dApg1s; sdkSilent=1742513644409; mtop_partitioned_detect=1; _m_h5_tk=0205fb81c63e4e357d47003aa2fdc9ce_1742434870100; _m_h5_tk_enc=2e8fef823d531d8aee27ad75079801fe; cookie2=25a679a2b59f7fb3f4e3cb94414f3a96; sgcookie=E100Y4V17ETmhzfdAl0KSB3FBYcE39eT%2Bh4KBTZjTorJUBGeePhrRfbLgXEeK%2BI%2FORneQqoLNUOP2DBQzEh4DWakNbvUka3Fd0TgQUteKydulRgvNO2EQBOiUwR9mPWX%2FEgQ; csg=e0c79423; tfstk=g8RxBjcge4UYTI1nijMuseNqt20kBCL2nn8QsGj0C3KJRercCIfDXRKD7hXs0sA92FtKuNm2srJyxeNDix5g6s5N1DmntXb2u156qPTFWoS5RwlGl5_fg_wBmEhKtXY2lrbj-UGHiDqkrij11t61F7sPW5s6ftwWPg7N5o__G4L54g_bGS61N__CSRaXf1gJPg711ZTrcYIahMV9dzUtUM0apJwBwZBAX5jz66d4tTIQqgPT6nqRhMGh25N6wZTuzgb_GXIWndOcNIi7A_TeEn_R9jEFkLTp29Auq5fBL3dOdHgg3axv0I7eeDFViepWiTRIqS-9-ndOKncSlh5f5hWesDPVcFTeTpfKMk7vFeKRKQquTg79tBCyPkjdS-g-yRyNhaztZr9WkX_iWaInrZ2aQTHPyM0-ARw_YGQRx42LQRWrl',
}

params = {
    'jsv': '2.7.2',
    'appKey': '34839810',
    't': '1742428029512',
    'sign': 'e8c6002d29b8eef4bbb81d437ff3fcb5',
    'v': '1.0',
    'type': 'originaljson',
    'accountSite': 'xianyu',
    'dataType': 'json',
    'timeout': '20000',
    'api': 'mtop.taobao.idlemtopsearch.pc.search',
    'sessionOption': 'AutoLoginOnly',
    'spm_cnt': 'a21ybx.search.0.0',
    'spm_pre': 'a21ybx.home.searchInput.0',
}

data = {
    'data': '{"pageNumber":1,"keyword":"iPhone14Pro美版","fromFilter":true,"rowsPerPage":30,"sortValue":"desc","sortField":"create","customDistance":"","gps":"","propValueStr":{"searchFilter":"quickFilter:filterPersonal;"},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}',
}

s = calculate_sign('0205fb81c63e4e357d47003aa2fdc9ce', '1742428029512', '34839810', data.get('data'))
print(s)

response = requests.post(
    'https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
    verify=False,
)