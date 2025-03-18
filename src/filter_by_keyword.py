import os
import time
import json
import requests
from PIL import Image
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from save_filtered_result import cache_feed_filtered_result
from product_detail import get_product_detail

def filter_by_keyword_lastest(driver, keyword):
    # del driver.requests

    time.sleep(3)
    print('等待搜索框 出现...')

    # 方法2：使用 form 内的第一个 input（假设这是搜索框）
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))
    )
    search_input.clear()
    search_input.send_keys(keyword)

    search_button = driver.find_element(By.XPATH, "//button[@type='submit' and .//img]")
    search_button.click()

    print('等待搜索结果...')
    del driver.requests

    time.sleep(2)
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.TAG_NAME, "body"))
    # )

    # page_source = driver.page_source

    search_api_request = None
    for request in driver.requests:
        # h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0
        print(request)
        if '/h5/mtop.taobao.idlemtopsearch.pc.search/1.0' in request.path and request.response:
            if request.response.status_code == 200 and 'application/json' in request.response.headers.get('Content-Type', ''):
                search_api_request = request
                break

    if search_api_request:
        response_body = search_api_request.response.body.decode('utf-8')
        response_json = json.loads(response_body)
        items = response_json.get('data').get('resultList')
    
        # cache_feed_filtered_result(items)
        for item_warpper in items:
            item_data = item_warpper.get('data').get('item').get('main').get('clickParam').get('args')
            # 提取字段
            item_id = str(item_data.get('item_id', ''))
            cookie_str = search_api_request.headers.get("Cookie")
            cookies = dict(cookie.split("=", 1) for cookie in cookie_str.split("; "))
            get_product_detail(cookies, search_api_request.headers, item_id)