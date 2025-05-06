from src.logger.app_logger import app_logger as logger

iPhone_market_deal_prices = {
    "iPhone 12 Mini": {"deal_price": [300, 1100, 400, 800]},
    "iPhone 12": {"deal_price": [400, 1450, 400, 1100]},
    "iPhone 12 Pro": {"deal_price": [500, 2000, 500, 1200]},
    "iPhone 12 Pro Max": {"deal_price": [700, 2450, 600, 1400]},
    "iPhone 13 Mini": {"deal_price": [600, 1500, 400, 1300]},
    "iPhone 13": {"deal_price": [700, 2800, 700, 1400]},
    "iPhone 13 Pro": {"deal_price": [1400, 3200, 100, 1900]},
    "iPhone 13 Pro Max": {"deal_price": [1500, 3700, 150, 2100]},
    "iPhone 14": {"deal_price": [1100, 2850, 400, 1700]},
    "iPhone 14 Plus": {"deal_price": [1200, 3200, 400 ,2000]},
    "iPhone 14 Pro": {"deal_price": [1800, 4350, 600, 2800]},
    "iPhone 14 Pro Max": {"deal_price": [1800, 5100, 800, 3300]},
    "iPhone 15": {"deal_price": [1800, 4200, 600, 2300]},
    "iPhone 15 Plus": {"deal_price": [1900, 4650, 800, 2700]},
    "iPhone 15 Pro": {"deal_price": [2900, 5800, 800, 3400]},
    "iPhone 15 Pro Max": {"deal_price": [3000, 6900, 1200, 3600]},
    "iPhone 16": {"deal_price": [2500, 5100, 900, 3500]},
    "iPhone 16 Plus": {"deal_price": [2800, 6300, 1000, 3800]},
    "iPhone 16 Pro": {"deal_price": [3200, 7800, 1600, 4500]},
    "iPhone 16 Pro Max": {"deal_price": [4500, 9000, 1800, 7000]},
}

def evaluate_iPhone_model_price_is_valid(name: str, 
                                         price, 
                                         transportFee, 
                                         quality: str, 
                                         repair_function: str,
                                         display_name: str):
    model_dict = iPhone_market_deal_prices.get(name)
    if not model_dict:
        logger.info(f'evaluate_iPhone_model_price_is_valid {name} 不存在')
        return False
    low, high, premium, _ = model_dict['deal_price']
    new_highest_price = high - 300
    total_price = price + transportFee
    if total_price > high:
        logger.info(f'evaluate_iPhone_model_price_is_valid {name} {total_price} 远高于市场价格: {high}')
        return False
    if (repair_function == '无任何维修' 
        or repair_function == ''
        or quality == '几乎全新' 
        or quality == '') and total_price <= new_highest_price:
        logger.info(f'{name} 价格: {total_price} 低于期望价格: {new_highest_price}，而且还是全新无维修 [成色: {quality} 拆修和功能: {repair_function} expected_price: {new_highest_price} price: {price} transportFee: {transportFee}, display_name: {display_name}]，大概率是假的，跳过')
        return False
    elif total_price <= low + premium:
        return True
                
