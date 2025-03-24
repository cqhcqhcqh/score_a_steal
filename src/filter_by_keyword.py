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
from .save_filtered_result import cache_feed_filtered_result, item_has_recommend, recommend_product
from .product_detail import get_product_detail
from .home_search_list import get_home_search_result
from .user_page_nav import goto_user_nav_page
from .user_page_product_list import fetch_user_product_list
from .deal_recommendation import DealRecommendationSystem

def filter_by_keyword_lastest(driver, keyword, expected_price=None, feishu_webhook=None, until_date=None):
    """
    根据关键词过滤最新商品，并保存到数据库
    使用连接池优化数据库性能
    
    新增功能：
    - 支持商品推荐系统
    - 可通过飞书推送通知
    """
    # del driver.requests

    time.sleep(3)
    print('等待搜索框 出现...')

    # 方法2：使用 form 内的第一个 input（假设这是搜索框）
    # todo 搜索框可能不出现 这里要加上重试
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
        # response_body = search_api_request.response.body.decode('utf-8')
        # response_json = json.loads(response_body)
        # items = response_json.get('data').get('resultList')

        # 获取公共信息
        cookie_str = search_api_request.headers.get("Cookie")
        cookies = dict(cookie.split("=", 1) for cookie in cookie_str.split("; "))
        headers = search_api_request.headers
        del headers['accept-encoding']
        headers['pragma'] = 'no-cache'

        recommendation_system = DealRecommendationSystem(
            feishu_webhook=feishu_webhook,
            min_seller_score=70,  # 可以根据需要调整阈值
            min_matching_score=75
        )
        pageNumber = 1
        # 获取搜索结果
        while result := get_home_search_result(cookies, headers, keyword, pageNumber):
            items, hasMore = result
            if hasMore:
                pageNumber += 1
            
            print(f'当前页: {pageNumber}, 找到 {len(items)} 个搜索结果')
            recommned_product_if_needed(recommendation_system, items, cookies, headers, expected_price)
        # 如果提供了期望价格，则使用推荐系统
    else:
        print("未找到搜索API请求")
        return 0

def recommned_product_if_needed(recommendation_system, items, cookies, headers, expected_price):
    processed_count = 0
    if expected_price is not None:
        print(f"使用推荐系统，期望价格: {expected_price}")
        # 处理每个商品
        for i, item_wrapper in enumerate(items):
            try:
                item_data = item_wrapper.get('data', {}).get('item', {}).get('main', {}).get('clickParam', {}).get('args', {})
                
                # 提取商品ID
                item_id = str(item_data.get('item_id', ''))
                if not item_id:
                    print(f"[{i+1}/{len(items)}] 商品ID不存在，跳过")
                    continue
                
                # 如果已经推送过，跳过
                if item_id in recommendation_system.notified_items:
                    print(f"[{i+1}/{len(items)}] 商品 {item_id} 已推送过，跳过")
                    continue
                
                print(f"\n[{i+1}/{len(items)}] 评估商品: {item_id}")
                
                # 获取商品详情
                product_detail = get_product_detail(cookies, headers, item_id)
                if not product_detail:
                    print(f"无法获取商品 {item_id} 的详情，跳过")
                    continue
                
                # 提取卖家ID
                seller_id = product_detail.seller_id
                
                if not seller_id:
                    print(f"商品 {item_id} 无卖家信息，跳过")
                    continue

                # 获取卖家信息
                user_info = goto_user_nav_page(cookies, headers, seller_id)
                
                if not user_info:
                    print(f"无法获取卖家 {seller_id} 的信息，跳过")
                    continue
                else:
                    print(f'kc_user_id: {user_info.kc_user_id} user_name: {user_info.display_name}')
                
                # 获取卖家的其他在售商品
                user_card_list = fetch_user_product_list(cookies, headers, seller_id)

                # 确保在会话上下文中调用
                # cache_feed_filtered_result(product_detail, user_info, user_card_list)
                price = product_detail.price + product_detail.transportFee
                if (product_detail.repair_function == '无任何维修' or not product_detail.repair_function
                    or product_detail.quality == '几乎全新' or not product_detail.quality) and price < expected_price:
                        print(f'价格低于期望价格，而且还是全新无维修，大概率是假的，跳过 {user_info.display_name}')
                elif not item_has_recommend(item_id) and price <= expected_price:
                    print(f'找到期望价格的商品')
                    recommend_product(item_id)
                    recommendation_system.notifier.send_deal_notification(product_detail, user_info)
                else:
                    print(f'价格高于期望价格，跳过')
                # 添加短暂延迟，避免请求过于频繁
                time.sleep(1)
            except Exception as db_err:
                print(f"保存数据到数据库时出错: {str(db_err)}")
            finally:
                processed_count += 1
            
            # 添加短暂延迟，避免请求过于频繁
            time.sleep(1)
    else:
        # 原有的处理逻辑(不使用推荐系统)
        for item_warpper in items:
            try:
                item_data = item_warpper.get('data', {}).get('item', {}).get('main', {}).get('clickParam', {}).get('args', {})
                # 提取字段
                item_id = str(item_data.get('item_id', ''))
                if not item_id:
                    print("商品ID不存在，跳过")
                    continue
                
                print(f"\n[{processed_count+1}/{len(items)}] 处理商品: {item_id}")
                
                # 获取商品详情
                product_detail = get_product_detail(cookies, headers, item_id).get('data', {})
                if not product_detail:
                    print(f"无法获取商品 {item_id} 的详情，跳过")
                    continue
                
                seller_id = str(product_detail.get('sellerDO', {}).get('sellerId', ''))
                if not seller_id:
                    print(f"商品 {item_id} 无卖家信息，跳过")
                    continue
                
                # 获取卖家个人页面信息
                user_info = goto_user_nav_page(cookies, headers, seller_id)
                
                # 获取卖家商品列表（支持分页）
                user_product_list = fetch_user_product_list(cookies, headers, seller_id)
                
                # 保存所有信息到数据库
                try:
                    cache_feed_filtered_result(product_detail, user_info, user_product_list)
                except Exception as db_err:
                    print(f"保存数据到数据库时出错: {str(db_err)}")
                
                processed_count += 1
                print(f"成功处理商品 {item_id}")
                
                # 添加短暂延迟，避免请求过于频繁
                time.sleep(1)
                
            except Exception as e:
                print(f"处理商品时出错: {str(e)}")
                continue
    
    print(f"\n===== 搜索完成，共处理 {processed_count}/{len(items)} 个商品 =====")
    return processed_count
