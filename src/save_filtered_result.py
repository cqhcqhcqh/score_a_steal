import json
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from product_detail import get_product_detail
from sqlalchemy import Column, Integer, String, DECIMAL, BigInteger, Boolean, create_engine

# 定义数据库模型
Base = declarative_base()

class ItemDetail(Base):
    __tablename__ = 'item_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, unique=True)
    detail_url = Column(String)
    price = Column(DECIMAL)
    is_free_shipping = Column(Boolean)
    want_count = Column(Integer)
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
    seller_id = Column(String)
    publish_time = Column(BigInteger)
    title = Column(String)

    def __repr__(self):
        return f"<SearchResult(item_id='{self.item_id}', title='{self.title}', price={self.price})>"
    
def cache_feed_filtered_result(item_data, item_show_data):
    try:
        # 初始化 SQLite 数据库
        engine = create_engine('sqlite:///search_results.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # 提取并存储数据
        # 提取字段
        itemDO = item_data['itemDO']
        item_id = str(itemDO.get('itemId'))
        price = float(itemDO.get('soldPrice', 0))  # 假设单位为分，转为元
        want_count = itemDO.get('wantCnt', 0)
        desc = itemDO.get('desc')
        title = itemDO.get('title')

        publish_time = int(item_show_data.get('publishTime', 0)) // 1000

        itemCatDTO = itemDO.get('itemCatDTO')
        category_id = str(itemDO.get('categoryId'))
        channel_cat_id = str(itemCatDTO.get('channelCatId'))
        sellerDO = item_data['sellerDO']
        seller_id = str(sellerDO['sellerId'])

        # 从 serviceUtParams 提取额外信息
        cpvLabels = json.loads(itemDO.get('cpvLabels', '[]'))
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
        # 存储
        item_detail = ItemDetail(
            item_id=item_id, title=title, price=price,
            is_free_shipping=is_free_shipping, want_count=want_count,
            description=desc, brand=brand, storage=storage, model=model,
            version=version, RAM=RAM, quality=quality, repair_function=repair_function,
            category_id=category_id, channel_cat_id=channel_cat_id, seller_id=seller_id,
            publish_time=publish_time,
        )

        # 检查是否已存在，避免重复插入
        if not session.query(ItemDetail).filter_by(item_id=item_id).first():
            session.add(item_detail)
        
        # 提交到数据库
        session.commit()
        print(f"成功存储 1 条搜索结果到数据库")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        session.rollback()

    finally:
        # driver.quit()
        session.close()