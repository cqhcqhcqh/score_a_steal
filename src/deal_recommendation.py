import os
import time
import json
import requests
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from seller_evaluation import evaluate_seller_credibility, detect_lure_seller, calculate_item_matching_score
from notifier import FeiShuNotifier, console_notify
from product_detail import get_product_detail
from user_page_nav import goto_user_nav_page
from user_page_product_list import fetch_user_product_list
from home_search_list import get_home_search_result
from qr_login import setup_driver, load_persistent_cookies

class DealRecommendationSystem:
    """闲鱼好价推荐系统"""
    
    def __init__(self, feishu_webhook=None, min_seller_score=70, min_matching_score=75):
        """
        初始化推荐系统
        feishu_webhook: 飞书Webhook地址(可选)
        min_seller_score: 最低卖家可信度分数
        min_matching_score: 最低商品匹配度分数
        """
        self.feishu_webhook = feishu_webhook
        self.min_seller_score = min_seller_score
        self.min_matching_score = min_matching_score
        
        if feishu_webhook:
            self.notifier = FeiShuNotifier(feishu_webhook)
        else:
            self.notifier = None
        
        # 用于存储已通知的商品ID，避免重复推送
        self.notified_items = set()
    
    def search_and_evaluate(self, keyword, expected_price, product_type='iPhone', max_items=50):
        """
        搜索并评估商品
        keyword: 搜索关键词
        expected_price: 期望价格
        product_type: 产品类型，默认为iPhone
        max_items: 最大处理商品数量
        """
        print(f"开始搜索: {keyword}, 期望价格: {expected_price}")
        
        # 初始化浏览器
        driver = setup_driver()
        driver.get('https://www.goofish.com/')
        load_persistent_cookies(driver)
        driver.refresh()
        time.sleep(3)
        
        print('等待页面加载完成，准备搜索...')
        
        # 定位搜索框并输入关键词
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-input')]"))
        )
        search_input.clear()
        search_input.send_keys(keyword)
        
        search_button = driver.find_element(By.XPATH, "//button[@type='submit' and .//img]")
        search_button.click()
        
        print('等待搜索结果...')
        time.sleep(2)
        
        # 清除旧请求记录
        del driver.requests
        
        # 获取API请求
        search_api_request = None
        for request in driver.requests:
            if '/h5/mtop.taobao.idlemtopsearch.pc.search/1.0' in request.path and request.response:
                if request.response.status_code == 200 and 'application/json' in request.response.headers.get('Content-Type', ''):
                    search_api_request = request
                    break
        
        found_items = []
        
        if search_api_request:
            # 提取cookies和headers用于后续请求
            cookie_str = search_api_request.headers.get("Cookie")
            cookies = dict(cookie.split("=", 1) for cookie in cookie_str.split("; "))
            headers = search_api_request.headers
            
            # 获取搜索结果
            items = get_home_search_result(cookies, headers, keyword).get('data', {}).get('resultList', [])
            print(f'找到 {len(items)} 个搜索结果')
            
            # 限制处理数量
            items = items[:min(max_items, len(items))]
            
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
                    if item_id in self.notified_items:
                        print(f"[{i+1}/{len(items)}] 商品 {item_id} 已推送过，跳过")
                        continue
                    
                    print(f"\n[{i+1}/{len(items)}] 评估商品: {item_id}")
                    
                    # 获取商品详情
                    product_detail = get_product_detail(cookies, headers, item_id).get('data', {})
                    if not product_detail:
                        print(f"无法获取商品 {item_id} 的详情，跳过")
                        continue
                    
                    # 提取卖家ID
                    seller_id = str(product_detail.get('sellerDO', {}).get('sellerId', ''))
                    if not seller_id:
                        print(f"商品 {item_id} 无卖家信息，跳过")
                        continue
                    
                    # 获取卖家信息
                    user_info = goto_user_nav_page(cookies, headers, seller_id)
                    
                    # 获取卖家的其他在售商品
                    user_product_list = fetch_user_product_list(cookies, headers, seller_id, max_pages=2)
                    
                    # 1. 评估卖家可信度
                    seller_result = evaluate_seller_credibility(user_info)
                    seller_score = seller_result['score']
                    seller_analysis = seller_result['analysis']
                    
                    # 2. 检测是否为引流商家
                    is_lure, lure_analysis = detect_lure_seller(
                        product_detail, 
                        user_product_list, 
                        expected_price=expected_price,
                        product_type=product_type
                    )
                    
                    # 3. 计算商品匹配度
                    matching_result = calculate_item_matching_score(
                        product_detail,
                        expected_price=expected_price,
                        product_type=product_type
                    )
                    matching_score = matching_result['score']
                    matching_analysis = matching_result['analysis']
                    
                    # 合并评估结果
                    evaluation_result = {
                        'seller_score': seller_score,
                        'matching_score': matching_score,
                        'is_lure': is_lure,
                        'seller_analysis': seller_analysis,
                        'matching_analysis': matching_analysis,
                        'lure_analysis': lure_analysis
                    }
                    
                    # 显示评估结果
                    print(f"卖家可信度: {seller_score}/100")
                    print(f"商品匹配度: {matching_score}/100")
                    print(f"引流风险: {'是' if is_lure else '否'}")
                    
                    # 判断是否符合推荐条件
                    if (not is_lure and 
                        seller_score >= self.min_seller_score and 
                        matching_score >= self.min_matching_score):
                        
                        # 添加到发现列表
                        found_items.append({
                            'item_info': product_detail,
                            'seller_info': user_info,
                            'evaluation_result': evaluation_result
                        })
                        
                        # 通知用户
                        if self.notifier:
                            self.notifier.send_deal_notification(product_detail, user_info, evaluation_result)
                        else:
                            console_notify(product_detail, user_info, evaluation_result)
                        
                        # 记录已通知的商品ID
                        self.notified_items.add(item_id)
                        
                        print(f"发现优质商品: {product_detail.get('title', '未知商品')}")
                    else:
                        print(f"商品不满足推荐条件，跳过")
                    
                    # 添加短暂延迟，避免请求过于频繁
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"处理商品时出错: {str(e)}")
                    continue
        
        # 关闭浏览器
        driver.quit()
        
        print(f"\n===== 搜索完成，共找到 {len(found_items)} 个符合条件的商品 =====")
        return found_items

def run_recommendation(keyword, expected_price, feishu_webhook=None, product_type='iPhone'):
    """
    运行推荐系统
    keyword: 搜索关键词
    expected_price: 期望价格
    feishu_webhook: 飞书Webhook地址
    product_type: 产品类型
    """
    system = DealRecommendationSystem(feishu_webhook=feishu_webhook)
    return system.search_and_evaluate(keyword, expected_price, product_type=product_type)

if __name__ == '__main__':
    # 示例使用
    keyword = 'iPhone 14 Pro'
    expected_price = 5000  # 期望价格5000元
    
    # 可以设置飞书Webhook，若不设置则使用控制台输出
    feishu_webhook = None  # 'https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx'
    
    run_recommendation(keyword, expected_price, feishu_webhook) 