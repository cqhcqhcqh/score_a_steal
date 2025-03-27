import re
import json
from datetime import datetime
from collections import defaultdict
from src.logger.app_logger import app_logger as logger

def evaluate_seller_credibility(user_info):
    """
    根据用户信息评估卖家可信度
    user_info: 从mtop.idle.web.user.page.head接口获取的用户信息
    返回: 评分(0-100)和详细分析
    """
    credibility_score = 60  # 基础分数
    analysis = []
    
    try:
        # 提取关键信息
        base_info = user_info.get('data', {}).get('baseInfo', {})
        tags = base_info.get('tags', {})
        module = user_info.get('data', {}).get('module', {})
        ylz_tags = module.get('base', {}).get('ylzTags', [])
        
        # 检查实名认证
        if tags.get('real_name_certification_77', False):
            credibility_score += 10
            analysis.append("已实名认证 (+10)")
        else:
            analysis.append("未实名认证")
        
        # 检查芝麻信用认证
        if tags.get('idle_zhima_zheng', False):
            credibility_score += 10
            analysis.append("已芝麻信用认证 (+10)")
        else:
            analysis.append("未芝麻信用认证")
        
        # 分析社交信息
        social = module.get('social', {})
        followers = int(social.get('followers', '0'))
        if followers > 100:
            credibility_score += 5
            analysis.append(f"粉丝数量较多: {followers} (+5)")
        
        # 分析用户标签
        if tags.get('alibaba_idle_playboy', False):
            credibility_score -= 10
            analysis.append("高风险标签: alibaba_idle_playboy (-10)")
        
        # 分析ylzTags中的信用等级
        for tag in ylz_tags:
            if tag.get('type') == 'ylzLevel':
                role = tag.get('attributes', {}).get('role')
                level = tag.get('attributes', {}).get('level', 0)
                if role == 'seller':
                    credibility_score += level * 2  # 假设每个等级加2分
                    analysis.append(f"卖家信用等级: {level} (+{level * 2})")
                elif role == 'buyer':
                    credibility_score += level  # 假设每个等级加1分
                    analysis.append(f"买家信用等级: {level} (+{level})")
            
    except Exception as e:
        analysis.append(f"评估过程出错: {str(e)}")
        
    return {
        "score": max(0, min(100, credibility_score)),  # 确保分数在0-100之间
        "analysis": analysis
    }

def detect_lure_seller(current_item, user_products, expected_price=None, product_type='iPhone'):
    """
    检测是否为引流商家
    current_item: 当前浏览的商品详情
    user_products: 该用户在售的其他商品列表
    expected_price: 用户期望价格
    product_type: 产品类型，默认为iPhone
    
    返回: 是否为引流商家(True/False)和详细分析
    """
    analysis = []
    
    # 过滤出同类产品
    similar_products = []
    for product in user_products:
        title = product.get('title', '').lower()
        if product_type.lower() in title:
            similar_products.append(product)
    
    # 如果有多个同类产品，可能是商家
    if len(similar_products) >= 3:
        analysis.append(f"卖家有 {len(similar_products)} 个{product_type}在售，可能是商家")
    
    # 分析价格异常
    if current_item and 'price' in current_item:
        # 当前商品价格
        current_price = float(current_item.get('price', 0))
        
        # 对比用户期望价格
        if expected_price and current_price < expected_price * 0.7:
            analysis.append(f"当前商品价格({current_price})远低于期望价格({expected_price})，可能是引流")
            return True, analysis
        
        # 分析卖家所有同类商品的价格差异
        if similar_products:
            prices = [float(p.get('price', 0)) for p in similar_products if 'price' in p]
            if prices:
                avg_price = sum(prices) / len(prices)
                # 如果当前价格比卖家其他同类商品平均价格低很多
                if current_price < avg_price * 0.7:
                    analysis.append(f"当前商品价格({current_price})远低于卖家其他同类商品均价({avg_price:.2f})，可能是引流")
                    return True, analysis
    
    # 分析商品描述是否有诱导性词汇
    if current_item and 'description' in current_item:
        desc = current_item.get('description', '').lower()
        lure_keywords = ['微信', '加我', 'v信', '私聊', '便宜', '更多', '联系我']
        found_keywords = [kw for kw in lure_keywords if kw in desc]
        if found_keywords:
            analysis.append(f"商品描述中含有引流关键词: {', '.join(found_keywords)}")
            return True, analysis
    
    return False, analysis

def calculate_item_matching_score(current_item, expected_price=None, product_type='iPhone'):
    """
    计算当前商品的匹配度评分
    current_item: 当前商品详情
    expected_price: 用户期望价格
    product_type: 产品类型，默认为iPhone
    
    返回: 匹配度评分(0-100)和详细分析
    """
    matching_score = 60  # 基础分数
    analysis = []
    
    try:
        # 检查商品名称是否符合产品类型
        title = current_item.get('title', '').lower()
        if product_type.lower() in title:
            matching_score += 10
            analysis.append(f"商品名称包含{product_type} (+10)")
        else:
            matching_score -= 20
            analysis.append(f"商品名称不包含{product_type} (-20)")
        
        # 检查价格是否在合理范围内
        if 'price' in current_item and expected_price:
            price = float(current_item.get('price', 0))
            
            # 价格接近期望价格(±10%)
            if 0.9 * expected_price <= price <= 1.1 * expected_price:
                matching_score += 20
                analysis.append(f"价格({price})非常接近期望价格({expected_price}) (+20)")
            # 价格低于期望价格但在合理范围内(10%-30%)
            elif 0.7 * expected_price <= price < 0.9 * expected_price:
                matching_score += 10
                analysis.append(f"价格({price})低于期望价格({expected_price})但在合理范围内 (+10)")
            # 价格远低于期望价格(>30%)
            elif price < 0.7 * expected_price:
                matching_score -= 15
                analysis.append(f"价格({price})远低于期望价格({expected_price})，可能有风险 (-15)")
        
        # 检查商品状态(全新/二手)
        if 'productStatus' in current_item:
            status = current_item.get('productStatus')
            if status == '全新':
                matching_score += 5
                analysis.append("商品全新 (+5)")
        
    except Exception as e:
        analysis.append(f"评估过程出错: {str(e)}")
        
    return {
        "score": max(0, min(100, matching_score)),  # 确保分数在0-100之间
        "analysis": analysis
    }

def extract_product_info(title):
    """
    从商品标题中提取成色、型号、版本和存储信息
    """
    # 使用正则表达式提取信息
    model_match = re.search(r'(\b(?:iPhone|苹果)\s?\d+\s?\w*\b)', title, re.IGNORECASE)
    storage_match = re.search(r'(\d+G)', title, re.IGNORECASE)
    version_match = re.search(r'(国行|有锁|无锁)', title, re.IGNORECASE)
    quality_match = re.search(r'(全新|几乎全新|良好|一般)', title, re.IGNORECASE)
    
    model = model_match.group(1) if model_match else None
    storage = storage_match.group(1) if storage_match else None
    version = version_match.group(1) if version_match else None
    quality = quality_match.group(1) if quality_match else None
    
    return model, storage, version, quality

def calculate_average_prices_from_listings(listings):
    """
    根据商品列表计算不同组合下的平均价格
    """
    price_data = defaultdict(list)
    
    for listing in listings:
        title = listing.get('title', '')
        price = float(listing.get('price', 0))
        
        model, storage, version, quality = extract_product_info(title)
        
        if model and storage and version and quality:
            key = (model, storage, version, quality)
            price_data[key].append(price)
    
    average_prices = {}
    for key, prices in price_data.items():
        average_prices[key] = sum(prices) / len(prices)
    
    return average_prices

# 示例用法
listings = [
    {"title": "苹果14pro国行128g全原装无拆修", "price": 5000},
    {"title": "苹果14pro国行128g全新", "price": 5200},
    {"title": "苹果14pro港版128g几乎全新", "price": 4800},
    # 添加更多商品数据
]

average_prices = calculate_average_prices_from_listings(listings)
for key, avg_price in average_prices.items():
    logger.info(f"组合: {key}, 平均价格: ¥{avg_price:.2f}") 