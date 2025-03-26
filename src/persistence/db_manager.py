import threading
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session

class DatabaseManager:
    """
    数据库连接管理器，实现单例模式的连接池和会话管理
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_url=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_url=None):
        if self._initialized:
            return
            
        # 默认使用SQLite数据库
        self.db_url = db_url or 'sqlite:///search_results.db'
        
        # 创建引擎，配置连接池
        self.engine = create_engine(
            self.db_url,
            pool_size=5,  # 连接池大小
            max_overflow=10,  # 最大溢出连接数
            pool_recycle=3600,  # 连接回收时间(秒)
            echo=False  # 是否输出SQL语句
        )
        
        # 创建会话工厂
        self.session_factory = sessionmaker(bind=self.engine)
        
        # 创建线程安全的会话管理
        self.Session = scoped_session(self.session_factory)
        
        self._initialized = True
    
    def get_engine(self):
        """获取数据库引擎"""
        return self.engine
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def create_all_tables(self, base):
        """创建所有表"""
        base.metadata.create_all(self.engine)
    
    @contextmanager
    def session_scope(self):
        """提供会话上下文管理器，自动处理提交和回滚"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

# 使用示例:
# 导入 Base 后创建表:
# from save_filtered_result import Base
# db_manager.create_all_tables(Base)
# 
# 使用会话:
# with db_manager.session_scope() as session:
#     session.add(some_object)
#     # 无需手动commit，上下文管理器会处理 