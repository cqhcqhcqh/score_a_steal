from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, Text, ForeignKey

engine = create_engine('sqlite:///test_seach_result.db')
Base = declarative_base()

class ItemDetail(Base):
    __tablename__ = 'item_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String, unique=True)
    seller_id = Column(String, ForeignKey('seller_info.seller_id'))
    seller = relationship("SellerInfo", back_populates="items")

class SellerInfo(Base):
    __tablename__ = 'seller_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(String, unique=True)
    items = relationship("ItemDetail", back_populates="seller")

    def update_from(self, other):
        """用另一个对象更新当前对象"""
        for key, value in other.__dict__.items():
            if key != 'id' and not key.startswith('_'):  # 排除 id 和内部属性
                setattr(self, key, value)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

for i in range(0, 2):
    seller = SellerInfo(seller_id=f'seller_id_{i}')
    if existSeller := session.query(SellerInfo).filter_by(seller_id=seller.seller_id).first():
        seller.id = existSeller.id
    session.merge(seller)

session.commit()

print(seller.seller_id)


session = Session()
for j in range(0, 3):
    item = ItemDetail(item_id=f'item_id_{j}', seller_id=f'seller_id_{j}')
    if existItem := session.query(ItemDetail).filter_by(item_id=item.item_id).first():
        item.id = existItem.id
    session.merge(item)
session.commit()

print(item.seller)