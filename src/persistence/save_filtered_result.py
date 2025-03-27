import json
from src.persistence.db_manager import db_manager
from src.logger.app_logger import app_logger as logger
from src.model.models import ItemDetail, SellerInfo

def cache_feed_filtered_result(item_data, seller_info=None, user_items=None):
    """
    缓存商品详情、卖家信息和其他商品列表到数据库
    使用db_manager进行连接管理
    """
    try:
        with db_manager.session_scope() as session:
            # 因为 ItemDetail 有一个外键 seller_id 指向 SellerInfo，所以需要先合并 SellerInfo
            try:
                logger.info(f"准备添加用户信息 {seller_info.seller_id} {seller_info.display_name} 到数据库")
                if not session.query(SellerInfo).filter_by(seller_id=seller_info.seller_id).first():
                    session.add(seller_info)
                logger.info(f"已添加用户信息 {seller_info.seller_id} {seller_info.display_name} 到数据库")
            except Exception as e:
                logger.info(f"添加用户信息 {seller_info.seller_id} {seller_info.display_name} 到数据库失败: {str(e)}")
            finally:
                logger.info(f"准备添加用户信息 {seller_info.seller_id} {seller_info.display_name} 到数据库结束")

            try:
                logger.info(f"准备添加新商品 {item_data.item_id} 到数据库")
                if existing_item_detail := session.query(ItemDetail).filter_by(item_id=item_data.item_id).first():
                    item_data.id = existing_item_detail.id
                session.merge(item_data)
                logger.info(f"已添加新商品 {item_data.item_id} 到数据库")
            except Exception as e:
                logger.info(f"添加新商品 {item_data.item_id} 到数据库失败: {str(e)}")
            finally:
                logger.info(f"添加新商品 {item_data.item_id} 到数据库结束")

            try:
                logger.info(f"准备添加用户商品卡片列表 到数据库")
                for item in user_items:
                    logger.info(f'准备添加用户商品卡片 item_id: {item.item_id}到数据库')
                    if item_data.item_id == item.item_id:
                        continue
                    if exist_card_item := session.query(ItemDetail).filter_by(item_id=item.item_id).first():
                        item.id = exist_card_item.id
                    session.merge(item)
                logger.info(f"已添加用户商品卡片列表 到数据库")
            except Exception as e:
                logger.info(f"添加用户商品卡片列表 到数据库失败: {str(e)}")
            finally:
                logger.info(f"添加用户商品卡片列表 到数据库结束")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.info(f"发生错误: {str(e)}")
        # 异常处理已在session_scope中完成，无需额外处理

# item_id 之前是否被标记为推荐商品，但是商品信息发生变化了，重新标记为可推荐商品
def recommend_product_did_changed(item_id):
    with db_manager.session_scope() as session:
        item_detail = session.query(ItemDetail).filter_by(item_id=item_id).first()
        if item_detail:
            logger.info(f"recommend_product_did_changed item_id: {item_id} share_url: {item_detail.share_url}  商品信息发生变化了，重新标记为推荐商品")
            item_detail.recommend_status = 0
        else:
            raise Exception(f"recommend_product_did_changed 未找到商品ID为 {item_id} 的商品")

# 将 item_id 标记为推荐商品
def recommend_product(item_id):
    with db_manager.session_scope() as session:
        item_detail = session.query(ItemDetail).filter_by(item_id=item_id).first()
        if item_detail:
            item_detail.recommend_status = 1
            logger.info(f"recommend_product item_id: {item_id} share_url: {item_detail.share_url}  已经被标记为推荐商品")
        else:
            logger.info(f"recommend_product 未找到商品ID为 {item_id} 的商品")

# item_id 之前是否被标记为推荐商品
def item_has_recommend(item_id):
    with db_manager.session_scope() as session:
        item_detail = session.query(ItemDetail).filter_by(item_id=item_id).first()
        if item_detail:
            return item_detail.recommend_status == 1
        else:
            return False

# item_data 是否需要入库，或者是否需要更新
def is_item_detail_need_add_or_update_in_db(item_data):
    with db_manager.session_scope() as session:
        try:
            logger.info(f"准备添加新商品 {item_data.item_id} 到数据库")
            if existing_item_detail := session.query(ItemDetail).filter_by(item_id=item_data.item_id).first():
                # 检查关键字段是否发生变化
                fields_changed = []
                if existing_item_detail.price != item_data.price:
                    fields_changed.append(f"价格从 {existing_item_detail.price} 变为 {item_data.price}")
                if existing_item_detail.want_count != item_data.want_count:
                    fields_changed.append(f"想要人数从 {existing_item_detail.want_count} 变为 {item_data.want_count}")
                if existing_item_detail.collect_count != item_data.collect_count:
                    fields_changed.append(f"收藏数量从 {existing_item_detail.collect_count} 变为 {item_data.collect_count}")
                if existing_item_detail.transportFee != item_data.transportFee:
                    fields_changed.append(f"运费从 {existing_item_detail.transportFee} 变为 {item_data.transportFee}")
                if existing_item_detail.description != item_data.description:
                    fields_changed.append("商品描述已更新")
                if existing_item_detail.title != item_data.title:
                    fields_changed.append("商品标题已更新")
                
                # 检查商品属性是否发生变化
                if existing_item_detail.brand != item_data.brand:
                    fields_changed.append(f"品牌从 {existing_item_detail.brand} 变为 {item_data.brand}")
                if existing_item_detail.model != item_data.model:
                    fields_changed.append(f"型号从 {existing_item_detail.model} 变为 {item_data.model}")
                if existing_item_detail.storage != item_data.storage:
                    fields_changed.append(f"存储容量从 {existing_item_detail.storage} 变为 {item_data.storage}")
                if existing_item_detail.RAM != item_data.RAM:
                    fields_changed.append(f"运行内存从 {existing_item_detail.RAM} 变为 {item_data.RAM}")
                    existing_item_detail.RAM = item_data.RAM
                if existing_item_detail.version != item_data.version:
                    fields_changed.append(f"版本从 {existing_item_detail.version} 变为 {item_data.version}")
                if existing_item_detail.quality != item_data.quality:
                    fields_changed.append(f"成色从 {existing_item_detail.quality} 变为 {item_data.quality}")
                if existing_item_detail.repair_function != item_data.repair_function:
                    fields_changed.append(f"拆修功能从 {existing_item_detail.repair_function} 变为 {item_data.repair_function}")
                
                # 检查分享信息是否发生变化
                if existing_item_detail.share_url != item_data.share_url:
                    fields_changed.append("分享链接已更新")
                if existing_item_detail.share_info != json.dumps(item_data.share_info, ensure_ascii=False):
                    fields_changed.append("分享信息已更新")
                
                # 图片信息更新
                if existing_item_detail.pic_url != item_data.pic_url:
                    fields_changed.append("商品主图已更新")
                    
                # 商品状态更新
                if existing_item_detail.item_status != item_data.item_status:
                    fields_changed.append(f"商品状态从 {existing_item_detail.item_status} 变为 {item_data.item_status}")
                
                if existing_item_detail.recommend_status != item_data.recommend_status:
                    fields_changed.append(f"商品推荐从 {existing_item_detail.recommend_status} 变为 {item_data.recommend_status}")

                if fields_changed:
                    logger.info(f"更新商品 {item_data.item_id} 的信息：")
                    for change in fields_changed:
                        logger.info(f"- {change}")
                    # recommend_product_did_changed(item_data.item_id)
                    # existing_item_detail.recommend_status = 0
                    return True
                else:
                    return False
            else:
                return True
        except Exception as e:
            logger.info(e)
        
def find_similar_products_by_seller(item_id):
    """
    根据商品ID查询卖家的所有类似商品，使用db_manager进行连接管理
    
    参数:
    item_id - 商品ID
    
    返回:
    卖家的所有类似商品列表
    """
    try:
        with db_manager.session_scope() as session:
            # 查询当前商品信息
            current_item = session.query(ItemDetail).filter_by(item_id=item_id).first()
            if not current_item:
                logger.info(f"未找到商品ID为 {item_id} 的商品")
                return []
                
            # 获取卖家ID
            seller_id = current_item.seller_id
            if not seller_id:
                logger.info(f"商品 {item_id} 没有关联卖家信息")
                return []
                
            # 获取卖家信息
            seller = session.query(SellerInfo).filter_by(seller_id=seller_id).first()
            if seller:
                logger.info(f"卖家: {seller.display_name}, 商铺ID: {seller.seller_id}")
            
            # 查询该卖家的所有商品
            all_seller_items = session.query(ItemDetail).filter_by(seller_id=seller_id).all()
            logger.info(f"卖家 {seller_id} 共有 {len(all_seller_items)} 件商品")
            
            # 提取当前商品的关键特征用于相似度匹配
            current_brand = current_item.brand
            current_model = current_item.model
            current_storage = current_item.storage
            current_category = current_item.category_id
            
            # 筛选类似商品
            similar_items = []
            for item in all_seller_items:
                # 跳过当前商品自身
                if item.item_id == item_id:
                    continue
                    
                # 计算相似度分数
                similarity_score = 0
                
                # 同品牌加分
                if current_brand and item.brand and current_brand.lower() == item.brand.lower():
                    similarity_score += 3
                    
                # 同型号加分
                if current_model and item.model and current_model.lower() == item.model.lower():
                    similarity_score += 5
                    
                # 同存储容量加分
                if current_storage and item.storage and current_storage.lower() == item.storage.lower():
                    similarity_score += 2
                    
                # 同类别加分
                if current_category and item.category_id and current_category == item.category_id:
                    similarity_score += 2
                    
                # 设置相似度阈值（至少一项相同）
                if similarity_score > 0:
                    similar_items.append({
                        'item': item,
                        'similarity_score': similarity_score
                    })
            
            # 按相似度降序排序
            similar_items.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # 格式化结果以便更好地展示
            result = []
            for item_data in similar_items:
                item = item_data['item']
                score = item_data['similarity_score']
                
                # 构建结果对象
                result.append({
                    'item_id': item.item_id,
                    'title': item.title,
                    'price': float(item.price) if item.price else 0,
                    'brand': item.brand,
                    'model': item.model,
                    'storage': item.storage,
                    'quality': item.quality,
                    'status': "在售" if item.item_status == 0 else "已售出",
                    'similarity_score': score,
                    'is_detail_info': item.is_detail_info,
                    'url': item.share_url
                })
                
            logger.info(f"找到 {len(result)} 件与商品 {item_id} 类似的商品")
            return result
            
    except Exception as e:
        logger.info(f"查询类似商品时发生错误: {str(e)}")
        return []

# 示例用法
def search_similar_items_example(item_id):
    """
    搜索类似商品的示例用法
    """
    similar_items = find_similar_products_by_seller(item_id)
    
    if not similar_items:
        logger.info("未找到类似商品")
        return
        
    logger.info("\n========== 类似商品列表 ==========")
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

def calculate_average_price(session, model, storage, version, quality):
    """
    计算给定组合下的平均价格
    """
    # 查询符合条件的商品
    items = session.query(ItemDetail).filter_by(
        model=model,
        storage=storage,
        version=version,
        quality=quality,
        item_status=0  # 仅计算在售商品
    ).all()
    
    # 计算平均价格
    if not items:
        return None
    
    total_price = sum(float(item.price) for item in items if item.price)
    average_price = total_price / len(items)
    return average_price

def is_lure_seller(session, current_item):
    """
    判断当前商品是否为引流商品
    """
    model = current_item.get('model')
    storage = current_item.get('storage')
    version = current_item.get('version')
    quality = current_item.get('quality')
    current_price = float(current_item.get('price', 0))
    
    # 计算平均价格
    average_price = calculate_average_price(session, model, storage, version, quality)
    
    if average_price is None:
        return False, "没有足够的数据计算平均价格"
    
    # 判断价格是否合理
    if current_price < average_price * 0.7:
        return True, f"当前商品价格({current_price})远低于市场平均价格({average_price:.2f})，可能是引流"
    
    return False, "价格合理"

# 示例用法
def evaluate_seller_items():
    with db_manager.session_scope() as session:
        # 假设 current_item 是从数据库或其他来源获取的商品详情
        current_item = {
            'model': 'iPhone 14 Pro',
            'storage': '128G',
            'version': '大陆国行',
            'quality': '几乎全新',
            'price': 5000  # 假设当前商品价格为5000元
        }
        
        is_lure, message = is_lure_seller(session, current_item)
        logger.info(message)