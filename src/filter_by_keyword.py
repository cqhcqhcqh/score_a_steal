import time
import random
from retry import retry
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from src.logger.app_logger import app_logger as logger
from src.api.user_page_nav import goto_user_nav_page
from src.api.product_detail import get_product_detail
from selenium.webdriver.support.ui import WebDriverWait
from src.api.home_search_list import get_home_search_result
from selenium.webdriver.support import expected_conditions as EC
from src.evaluation.deal_recommendation import DealRecommendationSystem
from src.persistence.save_filtered_result import cache_feed_filtered_result, item_has_recommend, is_item_detail_need_add_or_update_in_db
from src.api.user_page_product_list import fetch_user_product_list

@retry(exceptions=Exception, tries=5, delay=1, backoff=2)
def simulate_search_action_by_user(driver, keyword):
    time.sleep(random.uniform(3, 5))
    logger.info(f'等待搜索框 出现...')

    # 方法2：使用 form 内的第一个 input（假设这是搜索框）
    # todo 搜索框可能不出现 这里要加上重试
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))
    )
    search_input.clear()
    search_input.send_keys(keyword)

    search_button = driver.find_element(By.XPATH, "//button[@type='submit' and .//img]")
    search_button.click()

    logger.info(f'等待搜索结果...')
    del driver.requests

    time.sleep(random.uniform(3, 5))
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
    
    if search_api_request is None:
        raise Exception("未找到有效的搜索API请求")
    
    return search_api_request

def generate_valid_cookies_headers(driver, keyword):
    search_api_request = simulate_search_action_by_user(driver, keyword)
    # response_body = search_api_request.response.body.decode('utf-8')
    # response_json = json.loads(response_body)
    # items = response_json.get('data').get('resultList')

    # 获取公共信息
    cookie_str = search_api_request.headers.get("Cookie")
    cookies = dict(cookie.split("=", 1) for cookie in cookie_str.split("; "))
    headers = search_api_request.headers
    del headers['accept-encoding']
    # del headers['content-length']
    # del headers['cookie']
    return cookies, headers

def filter_by_keyword_lastest(driver,
                              keyword,
                              expected_price=None,
                              feishu_webhook=None,
                              in_days=2):
    """
    根据关键词过滤最新商品，并保存到数据库
    使用连接池优化数据库性能
    
    新增功能：
    - 支持商品推荐系统
    - 可通过飞书推送通知
    """
    cookies, headers = generate_valid_cookies_headers(driver, keyword)

    recommendation_system = DealRecommendationSystem(
        feishu_webhook=feishu_webhook,
        min_seller_score=70,  # 可以根据需要调整阈值
        min_matching_score=75
    )
    # loaded_cookies = driver.get_cookies()
    # loaded_cookies = {cookie['name']: cookie['value'] for cookie in loaded_cookies}
    # for key, value in cookies.items():
    #     if key not in loaded_cookies:
    #         loaded_cookies[key] = value
    # cookies = loaded_cookies
    pageNumber = 1
    # 获取搜索结果
    while result := get_home_search_result(cookies, headers, keyword, pageNumber):
        # cookies, headers = generate_valid_cookies_headers(driver, keyword)
        items, hasMore = result
        logger.info(f'当前页: {pageNumber}, 找到 {len(items)} 个搜索结果')
        res = recommned_product_if_needed(recommendation_system, 
                                            items, 
                                            cookies, 
                                            headers,
                                            expected_price, 
                                            pageNumber,
                                            in_days)
        if res == -1:
            break

        if hasMore:
            pageNumber += 1

def recommned_product_if_needed(recommendation_system,
                                items,
                                cookies,
                                headers,
                                expected_price,
                                pageNumber,
                                in_days):
    processed_count = 0
    if expected_price is not None:
        print(f"使用推荐系统，期望价格: {expected_price}")
        # 处理每个商品
        for i, item_wrapper in enumerate(items):
            try:
                item_data = item_wrapper.get('data', {}).get('item', {}).get('main', {}).get('clickParam', {}).get('args', {})
                publishTime = item_data.get('publishTime')
                published_time = datetime.fromtimestamp(float(publishTime) / 1000)
                current_time = datetime.now()
                desc = f'Page:{pageNumber} [{i+1}/{len(items)}] PT: {published_time.strftime("%Y-%m-%d %H:%M")}'
                if published_time + timedelta(days=in_days) < current_time:
                    return -1

                # 提取商品ID
                item_id = str(item_data.get('item_id', ''))
                if not item_id:
                    print(f"{desc} 商品ID不存在，跳过")
                    continue
                
                # 如果已经推送过，跳过
                if item_id in recommendation_system.notified_items:
                    print(f"{desc} 商品ID {item_id} 已推送过，跳过")
                    continue
                
                print(f"{desc} 评估商品: {item_id}")
                
                # 获取商品详情
                product_detail = get_product_detail(cookies, headers, item_id)
                if not product_detail:
                    print(f"无法获取商品 {item_id} 的详情，跳过")
                    continue

                if not is_item_detail_need_add_or_update_in_db(product_detail):
                    print(f"商品 {item_id} 已经落库，没有更新，无需再次评估")
                    continue
                
                # 提取卖家ID
                seller_id = product_detail.seller_id
                
                if not seller_id:
                    print(f"商品 {item_id} 无卖家信息，跳过")
                    continue

                # 获取卖家信息
                user_info = goto_user_nav_page(cookies, headers, seller_id)
                user_info.zhima_level_code = product_detail.zhima_level_code
                user_info.zhima_level_name = product_detail.zhima_level_name

                if not user_info:
                    print(f"无法获取卖家 {seller_id} 的信息，跳过")
                    continue
                else:
                    logger.info(f'kc_user_id: {user_info.kc_user_id} user_name: {user_info.display_name}')
                
                # 获取卖家的其他在售商品
                user_card_list = fetch_user_product_list(cookies, headers, seller_id)
                repair_function = product_detail.repair_function
                quality = product_detail.quality
                price = product_detail.price + product_detail.transportFee
                display_name = user_info.display_name
                if (repair_function == '无任何维修' 
                    or repair_function == ''
                    or quality == '几乎全新' 
                    or quality == '') and price <= expected_price:
                        logger.info(f'价格低于期望价格，而且还是全新无维修 [成色: {quality} 拆修和功能: {repair_function} expected_price: {expected_price} price: {product_detail.price} transportFee: {product_detail.transportFee}]，大概率是假的，跳过 display_name: [{display_name}]')
                elif not item_has_recommend(item_id) and price <= expected_price:
                    logger.info(f'找到期望价格的商品 [成色: {quality} 拆修和功能: {repair_function} expected_price: {expected_price} price: {product_detail.price} transportFee: {product_detail.transportFee}] display_name: [{display_name}]')
                    product_detail.recommend_status = 1
                    recommendation_system.notified_items.add(item_id)
                    recommendation_system.notifier.send_deal_notification(product_detail, user_info)
                else:
                    logger.info(f'价格高于期望价格，跳过')
                
                # 确保在会话上下文中调用
                cache_feed_filtered_result(product_detail, user_info, user_card_list)
                # 添加短暂延迟，避免请求过于频繁
                time.sleep(1)
            except Exception as db_err:
                import traceback
                traceback.print_exc()
                print(f"保存数据到数据库时出错: {str(db_err)}")
            finally:
                processed_count += 1
            
            # 添加短暂延迟，避免请求过于频繁
            time.sleep(random.uniform(2, 5))
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
                
                print(f"p: {pageNumber} n[{processed_count+1}/{len(items)}] 处理商品: {item_id}")
                
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
