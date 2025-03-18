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
    storage = Column(String)
    condition = Column(String)
    category_id = Column(String)
    seller_id = Column(String)
    publish_time = Column(BigInteger)
    keyword = Column(String)
    tagname = Column(String)

    def __repr__(self):
        return f"<SearchResult(item_id='{self.item_id}', title='{self.title}', price={self.price})>"
    
def cache_feed_filtered_result(items):
    try:
        # 初始化 SQLite 数据库
        engine = create_engine('sqlite:///search_results.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # 使用 BeautifulSoup 解析 HTML
        # soup = BeautifulSoup(page_source, 'html.parser')
        # with open ('search_feed_result.html', 'w+') as f:
        #     f.write(page_source)

        # items = soup.select('a[class*="feeds-item-wrap"]')

        # 提取并存储数据
        for item_warpper in items:
            item_data = item_warpper.get('data').get('item').get('main').get('clickParam').get('args')
            # 提取字段
            item_id = str(item_data.get('item_id', ''))
            # get_product_detail(dir)
            detail_url = f"https://www.goofish.com/item?id={item_id}"
            price = float(item_data.get('price', 0)) / 100  # 假设单位为分，转为元
            want_count = int(item_data.get('wantNum', 0))
            seller_id = item_data.get('seller_id', '')
            publish_time = int(item_data.get('publishTime', 0)) // 1000
            keyword = item_data.get('keyword', '')
            tagname = item_data.get('tagname', '')
            category_id = item_data.get('cCatId', '')

            # 从 serviceUtParams 提取额外信息
            service_params = json.loads(item_data.get('serviceUtParams', '[]'))
            brand, storage, condition = '', '', ''
            is_free_shipping = tagname == '包邮'
            description = keyword  # 临时使用 keyword 作为描述
            for param in service_params:
                args = param.get('args', {})
                content = args.get('content', '')
                description += content
                if 'freeShippingIcon' in content:
                    is_free_shipping = True
                elif '人想要' in content:
                    want_count = int(''.join(filter(str.isdigit, content)))

            # 存储
            item_detail = ItemDetail(
                item_id=item_id, detail_url=detail_url, price=price,
                is_free_shipping=is_free_shipping, want_count=want_count,
                description=description, brand=brand, storage=storage,
                condition=condition, category_id=category_id, seller_id=seller_id,
                publish_time=publish_time, keyword=keyword, tagname=tagname
            )

            # 检查是否已存在，避免重复插入
            if not session.query(ItemDetail).filter_by(item_id=item_id).first():
                session.add(item_detail)
        
        # 提交到数据库
        session.commit()
        print(f"成功存储 {len(items)} 条搜索结果到数据库")

    except Exception as e:
        print(f"发生错误: {str(e)}")
        session.rollback()

    finally:
        # driver.quit()
        session.close()