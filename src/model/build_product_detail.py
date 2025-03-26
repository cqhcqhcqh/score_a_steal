import json
from datetime import datetime
from src.model.models import ItemDetail

def build_product_detail(data):
    itemDO = data['itemDO']
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
    sellerDO = data['sellerDO']
    seller_id = str(sellerDO['sellerId'])
    # headerParams = shareInfo.get('contentParams').get('headerParams')
    # seller_city = headerParams.get('subTitle')
    # seller_xy_nickname = headerParams.get('title')
    transportFee = float(itemDO.get('transportFee', '0'))
    zhimaLevelInfo = sellerDO.get('zhimaLevelInfo')
    zhima_level_code = zhimaLevelInfo.get('levelCode')
    zhima_level_name = zhimaLevelInfo.get('levelName')

    # 图片信息
    image_infos = itemDO.get('imageInfos')
    if image_infos:
        pic_url = itemDO.get('imageInfos')[0].get('url')
    else:
        pic_url = data.get('trackParams').get('mainPic')
    if not pic_url:
        print(f'build_product_detail 主图找不到: {data}')
    image_infos = json.dumps(image_infos, ensure_ascii=False)
    # has_video = False  # 从详情页暂时无法确定是否有视频
    
    # 状态信息
    item_status = 0  # 默认在售
    if itemDO.get('status') == 'sold':
        item_status = 1
    auction_type = itemDO.get('auctionType', '')
    
    # 从 serviceUtParams 提取额外信息
    cpvLabels = itemDO.get('cpvLabels', [])
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

    return ItemDetail(
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
            # 添加分享相关字段
            share_url=shareUrl,
            share_info=json.dumps(shareInfo, ensure_ascii=False),
            # 商品图片信息
            pic_url=pic_url,
            image_infos=image_infos,
            item_status=item_status,
            auction_type=auction_type,
            zhima_level_code=zhima_level_code,
            zhima_level_name=zhima_level_name,
            updated_at=datetime.now()
        )