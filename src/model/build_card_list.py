from datetime import datetime
from src.model.models import ItemDetail
from src.logger.app_logger import app_logger as logger

def build_card_list(data, seller_id):
    card_list = data['cardList']
    
    card_items = []
    for card in card_list:
        card_data = card.get('cardData')
        other_item_id = card_data.get('id')
        
        # 跳过当前商品
        # if other_item_id == detail_item_id:
        #     continue
            
        detail_params = card_data.get('detailParams', {})
        other_title = detail_params.get('title', '')
        # print(card_data.get('priceInfo'), '-', detail_params.get('soldPrice'))
        # priceInfo = card_data.get('priceInfo').get('price')
        other_sold_price = detail_params.get('soldPrice', 0) or ''
        if '万' in other_sold_price:
            other_sold_price = float(other_sold_price.replace('万', '')) * 10000
        # logger.info(f'priceInfo: {priceInfo} other_sold_price: {other_sold_price}')
        other_detail_url = card_data.get('detailUrl', '')
        other_category_id = str(card_data.get('categoryId', ''))
        other_auction_type = card_data.get('auctionType', '')
        
        pic_info = card_data.get('picInfo', {})
        other_pic_url = pic_info.get('picUrl', '')
        
        item_status = card_data.get('itemStatus', 0)

        # 添加新商品
        card_item = ItemDetail(
            item_id=other_item_id,
            title=other_title,
            price=other_sold_price,
            seller_id=seller_id,
            detail_url=other_detail_url,
            category_id=other_category_id,
            auction_type=other_auction_type,
            item_status=item_status,
            pic_url=other_pic_url,
            updated_at=datetime.now()
        )
        card_items.append(card_item)
        
    return card_items