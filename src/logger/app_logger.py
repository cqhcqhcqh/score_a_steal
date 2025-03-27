import os
import sys
import logging
import json
from datetime import datetime
# from .log_watcher import send_to_dingtalk
# from settings.app_settings import app_settings

logger_initialized = False

class AlertFilter(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.ERROR:
            try:
                # format_record = {'environ': app_settings().app_environ,
                #                  'name': record.name,
                #                  'levelname': record.levelname,
                #                  'time': datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S,%f"),
                #                  'pathname': record.pathname,
                #                  'msg': record.msg}
                pass
                # send_to_dingtalk(format_record, app_settings().ding_talk_error_post_url, logger=app_logger)
            except Exception as e:
                app_logger.warning(f"send_to_dingtalk failed with exception: {repr(e)} record: {record}")
            # logger.info("额外操作：记录错误日志")
        # 返回True确保日志继续被处理
        # 没有开启 -O(Optimize) 或者 日志等级 >= WARN 都需要输出日志
        return __debug__ or record.levelno >= logging.DEBUG

class BaseFormatter(logging.Formatter):
    # 基础格式器，不包含颜色代码
    def format(self, record):
        levelname = record.levelname
        message = super().format(record)
        return f"{levelname}: {message}"
    
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # 蓝色
        "INFO": "\033[92m",  # 绿色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",  # 红色
        "CRITICAL": "\033[95m",  # 紫红色
    }
    RESET = "\033[0m"

    def __init__(self, fmt=None, datefmt=None, style='%', use_color=True):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_color = use_color

    def format(self, record):
        # sys.stdout.isatty() 这个函数的返回值仅仅反映了标准输出（即控制台）是否是一个终端类型的设备，而与file_handler没有任何关联。
        # 所以，当你的脚本在一个终端中运行时，sys.stdout.isatty()将返回True，即使日志消息是通过file_handler写入文件的
        if self.use_color and sys.stdout.isatty():
            levelname = record.levelname
            message = super().format(record)
            color = self.COLORS.get(levelname, self.RESET)
            return f"{color}{levelname}: {self.RESET}{message}"
        else:
            return super().format(record)

# 定义一个 JSON 格式化器
class JsonFormatter(logging.Formatter):
    def format(self, record):
        environ = "DEV"
        log_record = {
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
            "environ": environ,
            "message": record.getMessage()
        }

        # 添加异常信息，如果有的话
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info).replace('"', '')
        
        # 添加堆栈信息，如果有的话
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info).replace('"', '')

        return json.dumps(log_record, ensure_ascii=False).replace('\\"', '"').replace('"{', '{').replace('}"', '}').replace('"[', '[').replace(']"', ']')
    
def get_logger():
    # 创建或获取一个 logger
    logger = logging.getLogger("playground_logger")
    global logger_initialized
    if not logger_initialized:
        logger.addFilter(AlertFilter())
        logger.setLevel(logging.DEBUG)  # 设置全局最低日志级别

        # 创建一个流处理器（StreamHandler）输出到控制台
        stream_handler = logging.StreamHandler()

        if __debug__:
            log_directory = "log"
            log_file = os.path.join(log_directory, "app.log")
            # 检查日志文件夹是否存在，如果不存在则创建
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
            # 创建一个文件处理器（FileHandler）输出到文件
            file_handler = logging.FileHandler(log_file)

        # 设置带有日期时间的日志格式
        log_format = "%(asctime)s - %(name)s - %(message)s"
        # 日期时间格式，例如：2023-03-17 12:00:00
        date_format = "%Y-%m-%d %H:%M:%S"
        
        if __debug__:
            # 设置带有日期时间的日志格式
            # 创建一个日志格式器
            colored_formatter = ColoredFormatter(log_format, datefmt=date_format)
            # 将格式器设置给处理器
            stream_handler.setFormatter(colored_formatter)
        else:
            stream_handler.setFormatter(JsonFormatter())

        if __debug__:
            file_handler.setFormatter(BaseFormatter(log_format, datefmt=date_format))

        # 将处理器添加到 logger
        logger.addHandler(stream_handler)

        if __debug__:
            logger.addHandler(file_handler)

        logger_initialized = True
    return logger

app_logger = get_logger()

