import json
from datetime import datetime
from .db_manager import db_manager
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

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
    # seller_city = Column(String)
    # seller_xy_nickname = Column(String)
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
    
    updated_at = Column(DateTime, default=datetime.now)  # 更新时间
    
    recommend_status = Column(Integer)  # 0=未推荐，1=已推荐
    # 关系
    seller = relationship("SellerInfo", back_populates="items")

    def update_from(self, other):
        """用另一个对象更新当前对象"""
        for key, value in other.__dict__.items():
            if key != 'id' and not key.startswith('_'):  # 排除 id 和内部属性
                setattr(self, key, value)
                
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
    real_name_certification = Column(Boolean)
    xianyu_user_upgrade = Column(Boolean)
    idle_zhima_zheng = Column(Boolean)
    tb_xianyu_user = Column(Boolean)
    alibaba_idle_playboy = Column(Boolean)
    attentionPrivacyProtected = Column(Boolean)
    item_count = Column(Integer)
    rate = Column(String)
    seller_level = Column(Integer)
    seller_level_text = Column(String)
    buyer_level = Column(Integer)
    buyer_level_text = Column(String)

    # 社交信息
    followers_count = Column(String)
    following_count = Column(String)
    follow_status = Column(Integer)
        
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now)
    
    # 关系
    items = relationship("ItemDetail", back_populates="seller")

    def __repr__(self):
        return f"<SellerInfo(seller_id='{self.seller_id}', display_name='{self.display_name}')>"

db_manager.create_all_tables(Base)