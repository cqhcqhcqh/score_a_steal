import json
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from product_detail import get_product_detail
from datetime import datetime
from db_manager import db_manager

# 定义数据库模型
Base = declarative_base()

class ItemDetail(Base):
    __tablename__ = 'item_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, unique=True)
    detail_url = Column(String)
    price = Column(DECIMAL)
    transportFee = Column(DECIMAL)
    want_count = Column(Integer)
    collect_count = Column(Integer)
    description = Column(String)
    brand = Column(String)
    model = Column(String)
    storage = Column(String)
    RAM = Column(String)
    version = Column(String)
    quality = Column(String)
    repair_function = Column(String)
    category_id = Column(String)
    channel_cat_id = Column(String)
    seller_id = Column(String, ForeignKey('seller_info.seller_id'))
    publish_time = Column(DateTime)
    title = Column(String)
    seller_city = Column(String)
    seller_xy_nickname = Column(String)
    # 添加分享相关字段
    share_url = Column(String)  # 分享链接
    share_info = Column(String)  # 完整的分享信息（JSON字符串）
    
    # 商品图片信息
    pic_url = Column(String)  # 主图URL
    image_infos = Column(Text)  # 所有图片信息（JSON字符串）
    has_video = Column(Boolean, default=False)  # 是否有视频
    
    # 商品状态和类型
    item_status = Column(Integer)  # 0=在售，1=已售出
    auction_type = Column(String)  # 商品拍卖类型
    
    # 标签信息
    label_data = Column(Text)  # 标签数据（JSON字符串）
    service_ut_params = Column(Text)  # 服务参数
    
    # 数据来源和完整性
    is_detail_info = Column(Boolean, default=True)  # True=详细信息，False=简略信息（来自卖家商品列表）
    updated_at = Column(DateTime, default=datetime.now)  # 更新时间
    
    # 关系
    seller = relationship("SellerInfo", back_populates="items")

    def __repr__(self):
        return f"<SearchResult(item_id='{self.item_id}', title='{self.title}', desc='{self.description}, price={self.price}, seller={self.seller_xy_nickname})>"

class SellerInfo(Base):
    __tablename__ = 'seller_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(String, unique=True)
    encrypted_user_id = Column(String)
    kc_user_id = Column(String)
    display_name = Column(String)
    avatar_url = Column(String)
    ip_location = Column(String)
    is_self = Column(Boolean, default=False)
    
    # 社交信息
    followers_count = Column(String)
    following_count = Column(String)
    follow_status = Column(Integer)
    
    # 标签信息 (存储为JSON字符串)
    tags = Column(Text)
    ylz_tags = Column(Text)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now)
    
    # 关系
    items = relationship("ItemDetail", back_populates="seller")

    def __repr__(self):
        return f"<SellerInfo(seller_id='{self.seller_id}', display_name='{self.display_name}')>"

# 确保数据库表已创建
db_manager.create_all_tables(Base)

def cache_feed_filtered_result(item_data, user_info=None, user_items=None):
    """
    缓存商品详情、卖家信息和其他商品列表到数据库
    使用db_manager进行连接管理
    """
    try:
        with db_manager.session_scope() as session:
            # 提取并存储数据
            # 提取字段
            itemDO = item_data['itemDO']
            item_id = str(itemDO.get('itemId'))
            price = float(itemDO.get('soldPrice', 0))  # 假设单位为分，转为元
            want_count = itemDO.get('wantCnt', 0)
            collect_count = itemDO.get('collectCnt', 0)  # 添加收藏数量
            desc = itemDO.get('desc')
            title = itemDO.get('title')
            shareInfo = json.loads(itemDO.get('shareData').get('shareInfoJsonString'))
            shareUrl = shareInfo.get('url')
            # 将毫秒时间戳转换为 datetime 对象
            publish_time = datetime.fromtimestamp(int(itemDO.get('gmtCreate', 0)) // 1000)

            itemCatDTO = itemDO.get('itemCatDTO')
            category_id = str(itemDO.get('categoryId'))
            channel_cat_id = str(itemCatDTO.get('channelCatId'))
            sellerDO = item_data['sellerDO']
            seller_id = str(sellerDO['sellerId'])
            headerParams = shareInfo.get('contentParams').get('headerParams')
            seller_city = headerParams.get('subTitle')
            seller_xy_nickname = headerParams.get('title')
            transportFee = float(itemDO.get('transportFee', '0'))
            
            # 图片信息
            pic_url = itemDO.get('images', [{}])[0].get('url', '') if itemDO.get('images') else ''
            image_infos = json.dumps(itemDO.get('images', []), ensure_ascii=False)
            has_video = False  # 从详情页暂时无法确定是否有视频
            
            # 状态信息
            item_status = 0  # 默认在售
            if itemDO.get('status') == 'sold':
                item_status = 1
            auction_type = itemDO.get('auctionType', '')
            
            # 从 serviceUtParams 提取额外信息
            cpvLabels = itemDO.get('cpvLabels', '[]')
            brand, storage, model, version, RAM, quality, repair_function = '', '', '', '', '', '', ''
            
            # is_free_shipping = tagname == '包邮'
            # description = keyword  # 临时使用 keyword 作为描述
            for label in cpvLabels:
                # args = param.get('args', {})
                name = label.get('propertyName', '')
                value = label.get('valueName')
                # description += content
                if '品牌' == name:
                    brand = value
                elif '型号' == name:
                    model = value
                elif '存储容量' == name:
                    storage = value
                elif '运行内存' == name:
                    RAM = value
                elif '版本' == name:
                    version = value
                elif '成色' == name:
                    quality = value
                elif '拆修和功能' == name:
                    repair_function = value
                    
            # 处理卖家信息
            if user_info:
                # 提取卖家数据
                seller_info = session.query(SellerInfo).filter_by(seller_id=seller_id).first()
                
                data = user_info.get('data', {})
                base_info = data.get('baseInfo', {})
                encrypted_user_id = base_info.get('encryptedUserId', '')
                kc_user_id = base_info.get('kcUserId', '')
                is_self = base_info.get('self', False)
                tags_json = json.dumps(base_info.get('tags', {}), ensure_ascii=False)
                
                module = data.get('module', {})
                base = module.get('base', {})
                display_name = base.get('displayName', '')
                avatar_url = base.get('avatar', {}).get('avatar', '')
                ip_location = base.get('ipLocation', '')
                ylz_tags_json = json.dumps(base.get('ylzTags', []), ensure_ascii=False)
                
                social = module.get('social', {})
                followers_count = social.get('followers', '0')
                following_count = social.get('following', '0') 
                follow_status = social.get('followStatus', 0)
                
                if not seller_info:
                    seller_info = SellerInfo(
                        seller_id=seller_id,
                        encrypted_user_id=encrypted_user_id,
                        kc_user_id=kc_user_id,
                        display_name=display_name,
                        avatar_url=avatar_url,
                        ip_location=ip_location,
                        is_self=is_self,
                        followers_count=followers_count,
                        following_count=following_count,
                        follow_status=follow_status,
                        tags=tags_json,
                        ylz_tags=ylz_tags_json,
                        updated_at=datetime.now()
                    )
                    session.add(seller_info)
                else:
                    # 更新已有卖家信息
                    seller_info.encrypted_user_id = encrypted_user_id
                    seller_info.kc_user_id = kc_user_id
                    seller_info.display_name = display_name
                    seller_info.avatar_url = avatar_url
                    seller_info.ip_location = ip_location
                    seller_info.is_self = is_self
                    seller_info.followers_count = followers_count
                    seller_info.following_count = following_count
                    seller_info.follow_status = follow_status
                    seller_info.tags = tags_json
                    seller_info.ylz_tags = ylz_tags_json
                    seller_info.updated_at = datetime.now()
            
            # 处理卖家其他商品信息 - 改为与ItemDetail共用同一表结构
            if user_items and seller_id:
                data = user_items.get('data', {})
                card_list = data.get('cardList', [])
                
                for card in card_list:
                    card_data = card.get('cardData', {})
                    other_item_id = card_data.get('id')
                    
                    # 跳过当前商品
                    if other_item_id == item_id:
                        continue
                        
                    detail_params = card_data.get('detailParams', {})
                    other_title = detail_params.get('title', '')
                    other_sold_price = float(detail_params.get('soldPrice', 0))
                    other_detail_url = card_data.get('detailUrl', '')
                    other_category_id = str(card_data.get('categoryId', ''))
                    other_auction_type = card_data.get('auctionType', '')
                    
                    pic_info = card_data.get('picInfo', {})
                    other_pic_url = pic_info.get('picUrl', '')
                    other_has_video = pic_info.get('hasVideo', False)
                    
                    price_info = card_data.get('priceInfo', {})
                    other_price = float(price_info.get('price', 0))
                    
                    item_status = card_data.get('itemStatus', 0)
                    
                    # 标签数据
                    item_label_data = card_data.get('itemLabelDataVO', {})
                    label_data_json = json.dumps(item_label_data.get('labelData', {}), ensure_ascii=False)
                    service_ut_params = item_label_data.get('serviceUtParams', '{}')
                    
                    # 图片信息
                    image_infos = detail_params.get('imageInfos', '[]')
                    
                    # 商品信息提取
                    want_count_text = ''
                    if item_label_data and 'labelData' in item_label_data:
                        label_data = item_label_data.get('labelData', {})
                        for region in ['r1', 'r2', 'r3']:
                            if region in label_data:
                                for tag in label_data[region].get('tagList', []):
                                    if tag.get('data', {}).get('content', '').endswith('人想要'):
                                        want_count_text = tag.get('data', {}).get('content', '')
                    
                    other_want_count = 0
                    if want_count_text:
                        try:
                            other_want_count = int(want_count_text.replace('人想要', ''))
                        except:
                            pass
                    
                    # 检查该商品是否已存在
                    existing_other_item = session.query(ItemDetail).filter_by(item_id=other_item_id).first()
                    
                    if not existing_other_item:
                        # 添加新商品
                        other_item = ItemDetail(
                            item_id=other_item_id,
                            title=other_title,
                            price=other_price,
                            transportFee=0,  # 列表中无法获取运费信息
                            want_count=other_want_count,
                            collect_count=0,  # 列表中无法获取收藏数量
                            description="",  # 列表中无法获取描述
                            seller_id=seller_id,
                            detail_url=other_detail_url,
                            category_id=other_category_id,
                            auction_type=other_auction_type,
                            item_status=item_status,
                            pic_url=other_pic_url,
                            image_infos=image_infos,
                            has_video=other_has_video,
                            label_data=label_data_json,
                            service_ut_params=service_ut_params,
                            is_detail_info=False,  # 标记为简略信息
                            updated_at=datetime.now()
                        )
                        session.add(other_item)
                        print(f"从卖家列表添加新商品 {other_item_id} 到数据库")
                    else:
                        # 如果已存在并且是简略信息，则更新简略信息字段
                        if not existing_other_item.is_detail_info:
                            existing_other_item.title = other_title
                            existing_other_item.price = other_price
                            existing_other_item.want_count = other_want_count
                            existing_other_item.detail_url = other_detail_url
                            existing_other_item.category_id = other_category_id
                            existing_other_item.auction_type = other_auction_type
                            existing_other_item.pic_url = other_pic_url
                            existing_other_item.image_infos = image_infos
                            existing_other_item.has_video = other_has_video
                            existing_other_item.item_status = item_status
                            existing_other_item.label_data = label_data_json
                            existing_other_item.service_ut_params = service_ut_params
                            existing_other_item.updated_at = datetime.now()
                            print(f"更新卖家列表中的商品 {other_item_id} 信息")
            
            # 存储详细商品信息
            item_detail = ItemDetail(
                item_id=item_id, 
                title=title, 
                price=price,
                transportFee=transportFee, 
                want_count=want_count,
                collect_count=collect_count,
                description=desc, 
                brand=brand, 
                storage=storage, 
                model=model,
                version=version, 
                RAM=RAM, 
                quality=quality, 
                repair_function=repair_function,
                category_id=category_id, 
                channel_cat_id=channel_cat_id, 
                seller_id=seller_id,
                publish_time=publish_time, 
                seller_city=seller_city, 
                seller_xy_nickname=seller_xy_nickname,
                # 添加分享相关字段
                share_url=shareUrl,
                share_info=json.dumps(shareInfo, ensure_ascii=False),
                # 商品图片信息
                pic_url=pic_url,
                image_infos=image_infos,
                has_video=has_video,
                # 商品状态
                item_status=item_status,
                auction_type=auction_type,
                # 标记为详细信息
                is_detail_info=True,
                updated_at=datetime.now()
            )
            
            # 使用 merge 操作，如果记录存在则更新，不存在则插入
            existing_item = session.query(ItemDetail).filter_by(item_id=item_id).first()
            if existing_item:
                # 检查关键字段是否发生变化
                fields_changed = []
                if existing_item.price != price:
                    fields_changed.append(f"价格从 {existing_item.price} 变为 {price}")
                    item_detail.price = price
                if existing_item.want_count != want_count:
                    fields_changed.append(f"想要人数从 {existing_item.want_count} 变为 {want_count}")
                    item_detail.want_count = want_count
                if existing_item.collect_count != collect_count:
                    fields_changed.append(f"收藏数量从 {existing_item.collect_count} 变为 {collect_count}")
                    item_detail.collect_count = collect_count
                if existing_item.transportFee != transportFee:
                    fields_changed.append(f"运费从 {existing_item.transportFee} 变为 {transportFee}")
                    item_detail.transportFee = transportFee
                if existing_item.description != desc:
                    fields_changed.append("商品描述已更新")
                    item_detail.description = desc
                if existing_item.title != title:
                    fields_changed.append("商品标题已更新")
                    item_detail.title = title
                
                # 检查商品属性是否发生变化
                if existing_item.brand != brand:
                    fields_changed.append(f"品牌从 {existing_item.brand} 变为 {brand}")
                    item_detail.brand = brand
                if existing_item.model != model:
                    fields_changed.append(f"型号从 {existing_item.model} 变为 {model}")
                    item_detail.model = model
                if existing_item.storage != storage:
                    fields_changed.append(f"存储容量从 {existing_item.storage} 变为 {storage}")
                    item_detail.storage = storage
                if existing_item.RAM != RAM:
                    fields_changed.append(f"运行内存从 {existing_item.RAM} 变为 {RAM}")
                    item_detail.RAM = RAM
                if existing_item.version != version:
                    fields_changed.append(f"版本从 {existing_item.version} 变为 {version}")
                    item_detail.version = version
                if existing_item.quality != quality:
                    fields_changed.append(f"成色从 {existing_item.quality} 变为 {quality}")
                    item_detail.quality = quality
                if existing_item.repair_function != repair_function:
                    fields_changed.append(f"拆修功能从 {existing_item.repair_function} 变为 {repair_function}")
                    item_detail.repair_function = repair_function
                
                # 检查分享信息是否发生变化
                if existing_item.share_url != shareUrl:
                    fields_changed.append("分享链接已更新")
                    item_detail.share_url = shareUrl
                if existing_item.share_info != json.dumps(shareInfo, ensure_ascii=False):
                    fields_changed.append("分享信息已更新")
                    item_detail.share_info = json.dumps(shareInfo, ensure_ascii=False)
                
                # 图片信息更新
                if existing_item.pic_url != pic_url:
                    fields_changed.append("商品主图已更新")
                    item_detail.pic_url = pic_url
                    
                # 商品状态更新
                if existing_item.item_status != item_status:
                    fields_changed.append(f"商品状态从 {existing_item.item_status} 变为 {item_status}")
                    item_detail.item_status = item_status
                    
                if fields_changed:
                    print(f"更新商品 {item_id} 的信息：")
                    for change in fields_changed:
                        print(f"- {change}")
                        
                # 始终标记为详细信息
                item_detail.is_detail_info = True
            else:
                print(f"添加新商品 {item_id} 到数据库")
            
            session.merge(item_detail)
            
            print(f"成功存储商品、卖家和卖家其他商品信息到数据库")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        # 异常处理已在session_scope中完成，无需额外处理

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
                print(f"未找到商品ID为 {item_id} 的商品")
                return []
                
            # 获取卖家ID
            seller_id = current_item.seller_id
            if not seller_id:
                print(f"商品 {item_id} 没有关联卖家信息")
                return []
                
            # 获取卖家信息
            seller = session.query(SellerInfo).filter_by(seller_id=seller_id).first()
            if seller:
                print(f"卖家: {seller.display_name}, 商铺ID: {seller.seller_id}")
            
            # 查询该卖家的所有商品
            all_seller_items = session.query(ItemDetail).filter_by(seller_id=seller_id).all()
            print(f"卖家 {seller_id} 共有 {len(all_seller_items)} 件商品")
            
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
                    'url': item.share_url if item.share_url else item.detail_url
                })
                
            print(f"找到 {len(result)} 件与商品 {item_id} 类似的商品")
            return result
            
    except Exception as e:
        print(f"查询类似商品时发生错误: {str(e)}")
        return []

# 示例用法
def search_similar_items_example(item_id):
    """
    搜索类似商品的示例用法
    """
    similar_items = find_similar_products_by_seller(item_id)
    
    if not similar_items:
        print("未找到类似商品")
        return
        
    print("\n========== 类似商品列表 ==========")
    for idx, item in enumerate(similar_items, 1):
        status_text = item['status']
        detail_text = "详细信息" if item['is_detail_info'] else "简略信息"
        
        print(f"{idx}. {item['title']} ({status_text}, {detail_text})")
        print(f"   价格: ¥{item['price']:.2f}")
        if item['brand']:
            print(f"   品牌: {item['brand']}")
        if item['model']:
            print(f"   型号: {item['model']}")
        if item['storage']:
            print(f"   存储: {item['storage']}")
        if item['quality']:
            print(f"   成色: {item['quality']}")
        print(f"   相似度: {item['similarity_score']}")
        print(f"   链接: {item['url']}")
        print("-----------------------------------")
    
    print("=================================")