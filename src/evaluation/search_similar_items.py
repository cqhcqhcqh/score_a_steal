#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查询卖家类似商品的命令行工具
用法：
python search_similar_items.py 商品ID
"""
import argparse
from src.logger.app_logger import app_logger as logger
from src.persistence.save_filtered_result import find_similar_products_by_seller

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='查询卖家的类似商品')
    parser.add_argument('item_id', type=str, help='要查询的商品ID')
    parser.add_argument('--min-score', type=int, default=0, help='最低相似度分数，默认为0')
    parser.add_argument('--sort-by', choices=['similarity', 'price_asc', 'price_desc'], 
                        default='similarity', help='排序方式：相似度(默认)、价格升序或价格降序')
    parser.add_argument('--status', choices=['all', 'on_sale', 'sold'], 
                        default='all', help='商品状态：全部(默认)、在售或已售出')
    
    args = parser.parse_args()
    
    # 获取类似商品
    similar_items = find_similar_products_by_seller(args.item_id)
    
    if not similar_items:
        logger.info("未找到类似商品")
        return
    
    # 按状态过滤
    if args.status == 'on_sale':
        similar_items = [item for item in similar_items if item['status'] == '在售']
    elif args.status == 'sold':
        similar_items = [item for item in similar_items if item['status'] == '已售出']
    
    # 按最低相似度过滤
    similar_items = [item for item in similar_items if item['similarity_score'] >= args.min_score]
    
    # 根据选择的方式排序
    if args.sort_by == 'price_asc':
        similar_items.sort(key=lambda x: x['price'])
    elif args.sort_by == 'price_desc':
        similar_items.sort(key=lambda x: x['price'], reverse=True)
    # 默认已经按相似度排序，不需要再排序
    
    # 打印结果
    logger.info(f"\n========== 找到 {len(similar_items)} 件类似商品 ==========")
    for idx, item in enumerate(similar_items, 1):
        status_text = item['status']
        detail_text = "详细信息" if item['is_detail_info'] else "简略信息"
        
        logger.info(f"{idx}. {item['title']} ({status_text}, {detail_text})")
        logger.info(f"   价格: ¥{item['price']:.2f}")
        if item['brand']:
            logger.info(f"   品牌: {item['brand']}")
        if item['model']:
            logger.info(f"   型号: {item['model']}")
        if item['storage']:
            logger.info(f"   存储: {item['storage']}")
        if item['quality']:
            logger.info(f"   成色: {item['quality']}")
        logger.info(f"   相似度: {item['similarity_score']}")
        logger.info(f"   链接: {item['url']}")
        logger.info("-----------------------------------")
    
    logger.info("=================================")

if __name__ == "__main__":
    main() 