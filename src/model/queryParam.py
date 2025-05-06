from typing import Dict
from dataclasses import dataclass

@dataclass
class QueryModel:
    keyword: str
    within_days: int
    average_price: float
    expected_price: float
    notify_webhook_url: str = "https://open.feishu.cn/open-apis/bot/v2/hook/34e8583a-82e8-4b05-a1f5-6afce6cae815"

    def to_dict(self):
        return {
            "keyword": self.keyword,
            "expected_price": self.expected_price,
            "within_days": self.within_days,
            "average_price": self.average_price,
            "notify_webhook_url": self.notify_webhook_url
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class QueryModelFactory:
    DEFAULT_MODELS: Dict[str, dict] = {
        'steal_iPhone_Pro_256': {
            'keyword': '苹果 iPhone Pro',
            'within_days': 14,
            'average_price': 2499,
            'expected_price': 1600,
        },
        'steal_iPhone_14Pro_256': {
            'keyword': 'iPhone 14 Pro',
            'within_days': 14,
            'average_price': 2499,
            'expected_price': 1600,
        },
        'iPhone_14Pro_256_locked': {
            'keyword': 'iPhone 14 Pro 256 有锁',
            'within_days': 14,
            'average_price': 2800,
            'expected_price': 2500,
        },
        'iPhone_14Pro_256_unlocked': {
            'keyword': 'iPhone 14 Pro 256 无锁',
            'within_days': 14,
            'average_price': 2800,
            'expected_price': 2500,
        },
        'iPhone_14Pro_256_china': {
            'keyword': 'iPhone 14 Pro 256 国行',
            'within_days': 14,
            'average_price': 3500,
            'expected_price': 3000,
        },
        'iPhone_14_256_locked': {
            'keyword': 'iPhone 14 有锁 256',
            'within_days': 14,
            'average_price': 2200,
            'expected_price': 1800,
        },
        'iPhone_14_256_unlocked': {
            'keyword': 'iPhone 14 有锁 256',
            'within_days': 14,
            'average_price': 2500,
            'expected_price': 2000,
        },
        'iPhone_14_256_china': {
            'keyword': 'iPhone 14 国行 256',
            'within_days': 14,
            'average_price': 2500,
            'expected_price': 2000,
        }
    }

    @staticmethod
    def create(model_name: str) -> QueryModel:
        if model_name not in QueryModelFactory.DEFAULT_MODELS:
            raise ValueError(f'Unknow mode: {model_name}')
        return QueryModel(**QueryModelFactory.DEFAULT_MODELS[model_name])
    
    @staticmethod
    def get_all_models() -> Dict[str, QueryModel]:
        return {name : QueryModel(**data) for name, data in QueryModelFactory.DEFAULT_MODELS.items()}
    
    @staticmethod
    def stealiPhonePro256():
        return QueryModelFactory.create('steal_iPhone_Pro_256')
    
    @staticmethod
    def stealiPhone14Pro256():
        return QueryModelFactory.create('steal_iPhone_14Pro_256')
    
    @staticmethod
    def iPhone14Pro256Locked():
        return QueryModelFactory.create('iPhone_14Pro_256_locked')
    
    @staticmethod
    def iPhone14Pro256UnLocked():
        return QueryModelFactory.create('iPhone_14Pro_256_unlocked')