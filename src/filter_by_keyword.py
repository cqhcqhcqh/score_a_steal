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
from src.api.user_page_product_list import fetch_user_product_list
from src.evaluation.deal_recommendation import DealRecommendationSystem
from src.evaluation.evaluate_model import evaluate_iPhone_model_price_is_valid
from src.persistence.save_filtered_result import cache_feed_filtered_result, item_has_recommend, is_item_detail_need_add_or_update_in_db

@retry(exceptions=Exception, tries=5, delay=1, backoff=2)
def simulate_search_action_by_user(driver, keyword):
    logger.info('simulate_search_action_by_user')
    # time.sleep(random.uniform(3, 5))
    # logger.info(f'等待搜索框 出现...')

    # 方法2：使用 form 内的第一个 input（假设这是搜索框）
    # todo 搜索框可能不出现 这里要加上重试
    search_input = WebDriverWait(driver, 5, poll_frequency=1.0).until(
        lambda driver: (
            logger.info(f'查找`输入搜索框`...'),
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))(driver)
        )[1]
    )
    logger.info(f'找到`输入搜索框`...')
    search_input.clear()
    search_input.send_keys(keyword)
    
    search_button = WebDriverWait(driver, 5, poll_frequency=1.0).until(
        lambda driver: (
            logger.info(f'查找`search submit button`...'),
            EC.presence_of_element_located((By.XPATH, "//button[@type='submit' and .//img]"))(driver)
        )[1]
    ) 
    # driver.find_element(By.XPATH, "//button[@type='submit' and .//img]")
    logger.info(f'找到`search submit button`...')
    search_button.click()

    logger.info(f'等待搜索结果...')
    del driver.requests

    time.sleep(random.uniform(2, 4))
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.TAG_NAME, "body"))
    # )

    # page_source = driver.page_source

    search_api_request = None
    for request in driver.requests:
        # h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0
        logger.info(request)
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

def filter_by_keyword_lastest(driver, queryParams):
    """
    根据关键词过滤最新商品，并保存到数据库
    使用连接池优化数据库性能
    
    新增功能：
    - 支持商品推荐系统
    - 可通过飞书推送通知
    """
    # cookies, headers = None, None

    recommendation_system = DealRecommendationSystem(
        feishu_webhook=queryParams.notify_webhook_url,
        min_seller_score=70,  # 可以根据需要调整阈值
        min_matching_score=75
    )
    loaded_cookies = driver.get_cookies()
    headers = {
    "content-length": "407",
    "sec-ch-ua-platform": "\"macOS\"",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "accept": "application/json",
    "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua-mobile": "?0",
    "origin": "https://www.goofish.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.goofish.com/",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i",
  }
    loaded_cookies = {cookie['name']: cookie['value'] for cookie in loaded_cookies}
    # for key, value in cookies.items():
    #     if key not in loaded_cookies:
    #         loaded_cookies[key] = value
    cookies = loaded_cookies
    pageNumber = 1
    # 获取搜索结果
    while True:
        # cookies, headers = generate_valid_cookies_headers(driver, queryParams.keyword)
        result = get_home_search_result(cookies, headers, queryParams.keyword, pageNumber)
        items, hasMore = result
        logger.info(f'当前页: {pageNumber}, 找到 {len(items)} 个搜索结果')
        res = recommned_product_if_needed(recommendation_system, 
                                          driver,
                                          items, 
                                          cookies, 
                                          headers,
                                          queryParams.expected_price, 
                                          pageNumber,
                                          queryParams.within_days)
        if res == -1:
            break

        if hasMore:
            pageNumber += 1
        # else:
        #     break

def recommned_product_if_needed(recommendation_system,
                                driver,
                                items,
                                cookies,
                                headers,
                                expected_price,
                                pageNumber,
                                in_days):
    processed_count = 0
    if expected_price is not None:
        logger.info(f"使用推荐系统，期望价格: {expected_price}")
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
                    logger.info(f"{desc} 商品ID不存在，跳过")
                    continue
                
                # 如果已经推送过，跳过
                if item_id in recommendation_system.notified_items:
                    logger.info(f"{desc} 商品ID {item_id} 已推送过，跳过")
                    continue
                
                logger.info(f"{desc} 评估商品: {item_id}")
                
                try:
                # 获取商品详情
                    product_detail = get_product_detail(cookies, headers, item_id)
                except Exception as e:
                    auto_captcha(driver, item_id, item_data.get('cCatId'))
                    logger.info(f'get_product_detail failed with {e}')
                    continue

                if not product_detail:
                    logger.info(f"无法获取商品 {item_id} 的详情，跳过")
                    continue

                if not is_item_detail_need_add_or_update_in_db(product_detail):
                    logger.info(f"商品 {item_id} 已经落库，没有更新，无需再次评估")
                    continue
                
                # 提取卖家ID
                seller_id = product_detail.seller_id
                
                if not seller_id:
                    logger.info(f"商品 {item_id} 无卖家信息，跳过")
                    continue

                # 获取卖家信息
                user_info = goto_user_nav_page(cookies, headers, seller_id)
                user_info.zhima_level_code = product_detail.zhima_level_code
                user_info.zhima_level_name = product_detail.zhima_level_name

                if not user_info:
                    logger.info(f"无法获取卖家 {seller_id} 的信息，跳过")
                    continue
                else:
                    logger.info(f'kc_user_id: {user_info.kc_user_id} user_name: {user_info.display_name}')
                
                # 获取卖家的其他在售商品
                user_card_list = fetch_user_product_list(cookies, headers, seller_id)
                model = product_detail.model
                repair_function = product_detail.repair_function
                quality = product_detail.quality
                transportFee = product_detail.transportFee
                price = product_detail.price
                display_name = user_info.display_name
                if not item_has_recommend(item_id) and evaluate_iPhone_model_price_is_valid(model, 
                                                                                            price, 
                                                                                            transportFee, 
                                                                                            quality, 
                                                                                            repair_function,
                                                                                            display_name):
                    logger.info(f'找到期望价格的商品 {model} price: {price} [成色: {quality} 拆修和功能: {repair_function} expected_price: {expected_price} price: {product_detail.price} transportFee: {product_detail.transportFee}] display_name: [{display_name}]')
                    product_detail.recommend_status = 1
                    recommendation_system.notified_items.add(item_id)
                    recommendation_system.notifier.send_deal_notification(product_detail, user_info)
                else:
                    product_detail.impersonal = 1
                # if (repair_function == '无任何维修' 
                #     or repair_function == ''
                #     or quality == '几乎全新' 
                #     or quality == '') and price <= expected_price:
                #         logger.info(f'价格低于期望价格，而且还是全新无维修 [成色: {quality} 拆修和功能: {repair_function} expected_price: {expected_price} price: {product_detail.price} transportFee: {product_detail.transportFee}]，大概率是假的，跳过 display_name: [{display_name}]')
                # elif not item_has_recommend(item_id) and price <= expected_price:
                #     logger.info(f'找到期望价格的商品 [成色: {quality} 拆修和功能: {repair_function} expected_price: {expected_price} price: {product_detail.price} transportFee: {product_detail.transportFee}] display_name: [{display_name}]')
                #     product_detail.recommend_status = 1
                #     recommendation_system.notified_items.add(item_id)
                #     recommendation_system.notifier.send_deal_notification(product_detail, user_info)
                # else:
                #     logger.info(f'价格高于期望价格，跳过')
                
                # 确保在会话上下文中调用
                cache_feed_filtered_result(product_detail, user_info, user_card_list)
                # 添加短暂延迟，避免请求过于频繁
                time.sleep(1)
            except Exception as db_err:
                import traceback
                traceback.print_exc()
                logger.info(f"保存数据到数据库时出错: {str(db_err)}")
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
                    logger.info(f"商品ID不存在，跳过")
                    continue
                
                logger.info(f"p: {pageNumber} n[{processed_count+1}/{len(items)}] 处理商品: {item_id}")
                
                # 获取商品详情
                product_detail = get_product_detail(cookies, headers, item_id).get('data', {})
                if not product_detail:
                    logger.info(f"无法获取商品 {item_id} 的详情，跳过")
                    continue
                
                seller_id = str(product_detail.get('sellerDO', {}).get('sellerId', ''))
                if not seller_id:
                    logger.info(f"商品 {item_id} 无卖家信息，跳过")
                    continue
                
                # 获取卖家个人页面信息
                user_info = goto_user_nav_page(cookies, headers, seller_id)
                
                # 获取卖家商品列表（支持分页）
                user_product_list = fetch_user_product_list(cookies, headers, seller_id)
                
                # 保存所有信息到数据库
                try:
                    cache_feed_filtered_result(product_detail, user_info, user_product_list)
                except Exception as db_err:
                    logger.info(f"保存数据到数据库时出错: {str(db_err)}")
                
                processed_count += 1
                logger.info(f"成功处理商品 {item_id}")
                
                # 添加短暂延迟，避免请求过于频繁
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.info(f"处理商品时出错: {str(e)}")
                continue
    
    logger.info(f"\n===== 搜索完成，共处理 {processed_count}/{len(items)} 个商品 =====")
    return processed_count

from selenium.webdriver.common.action_chains import ActionChains

def auto_captcha(driver, item_id, cate_id=None):
    # driver.get(f'https://www.goofish.com/item?spm=a21ybx.home.feedsCnxh.1.4c053da6xuSmTf&id=906552072084&categoryId=126862528')
    driver.get(f'https://www.goofish.com/item?spm=a21ybx.home.feedsCnxh.1.4c053da6xuSmTf&id={item_id}&categoryId={cate_id}')
    slider = None
    
    time.sleep(random.uniform(3, 5))
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        logger.info(f'find quick_enter_button 找到 iframes')
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            slider = WebDriverWait(driver, 5, poll_frequency=1.0).until(
                lambda driver: (
                    logger.info(f'查找`captcha 滑块`...'),
                    EC.presence_of_element_located((By.CLASS_NAME, "btn_slide"))(driver)
                )[1]
            )
            slider_track = WebDriverWait(driver, 5, poll_frequency=1.0).until(
                lambda driver: (
                    logger.info(f'查找`captcha 滑块轨道`...'),
                    EC.presence_of_element_located((By.CLASS_NAME, "nc_scale"))(driver)
                )[1]
            )

    if not slider:
        return
    track_width = slider_track.size['width']
    slider_width = slider.size['width']
    # target_position = track_width - slider_width
    # logger.info(f'track_width: {track_width} slider_width: {slider_width} target_position: {target_position}')
    # driver.execute_script(f"""
    #     var slider = document.querySelector('.btn_slide');
    #     var event = new MouseEvent('mousedown', {{bubbles: true}});
    #     slider.dispatchEvent(event);
    #     slider.style.left = '{target_position}px';
    #     var event = new MouseEvent('mouseup', {{bubbles: true}});
    #     slider.dispatchEvent(event);
    # """)
    # 方法2：模拟人类拖动行为（更自然）
    actions = ActionChains(driver)
    actions.click_and_hold(slider)
    
    # # 分段移动，模拟人类行为
    # total_distance = slider_width + 20
    # steps = 3
    # for i in range(steps):
    #     distance = total_distance / steps
    #     actions.move_by_offset(distance, 0)
    #     time.sleep(random.uniform(0.01, 0.05))  # 添加小延迟模拟人类操作
    
    # actions.release()
    # actions.perform()
    human_like_slide(actions, slider, track_width)

    driver.switch_to.default_content()
    # 等待验证完成
    time.sleep(3)
    
    # slider_width = driver.find_element(By.CLASS_NAME, "nc_scale").size['width']
    # search_input = WebDriverWait(driver, 5, poll_frequency=1.0).until(
    #     lambda driver: (
    #         logger.info(f'查找`输入搜索框`...'),
    #         EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))(driver)
    #     )[1]
    # )

def human_like_slide(actions, slider, total_distance):
    actions.click_and_hold(slider)
    current = 0
    total_distance += 100
    while current < total_distance:
        step = random.randint(40, 80)  # 随机步长
        if current + step > total_distance:
            step = total_distance - current
        actions.move_by_offset(step, random.randint(-2, 2))  # 添加微小垂直偏移
        time.sleep(random.uniform(0.01, 0.05))  # 随机延迟
        current += step
    actions.release()
    actions.perform()