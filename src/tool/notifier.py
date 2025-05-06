import json
import requests
from datetime import datetime
from src.model.models import ItemDetail, SellerInfo
from src.logger.app_logger import app_logger as logger

class FeiShuNotifier:
    """飞书机器人通知类"""
    
    def __init__(self, webhook_url):
        """
        初始化飞书通知器
        webhook_url: 飞书机器人的Webhook地址
        """
        self.webhook_url = webhook_url
    
    def send_deal_notification(self, item_info: ItemDetail, seller_info: SellerInfo, evaluation_result: dict=None):
        """
        发送优质商品信息到飞书
        item_info: 商品信息
        seller_info: 卖家信息
        evaluation_result: 评估结果
        """
        try:
            # 提取商品关键信息
            title = item_info.title
            price = item_info.price
            item_id = item_info.item_id
            desc = item_info.description
            
            # 构建分享链接
            share_url = item_info.share_url
            
            # 提取卖家信息
            seller_name = seller_info.display_name
            
            # 提取评估结果
            seller_score = evaluation_result.get('seller_score', 0) if evaluation_result else 0     
            matching_score = evaluation_result.get('matching_score', 0) if evaluation_result else 0
            is_lure = evaluation_result.get('is_lure', False) if evaluation_result else False
            seller_analysis = evaluation_result.get('seller_analysis', []) if evaluation_result else []
            matching_analysis = evaluation_result.get('matching_analysis', []) if evaluation_result else []
            
            # 构建通知内容
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "商品详情"
                        },
                        "template": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**价格**: ¥{price}\n**卖家**: {seller_name}\n**发现时间**: {current_time}"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**商品描述**: {desc[:100]}..."
                            }
                        },
                        {
                            "tag": "hr"
                        },
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**评估结果**\n卖家可信度: {seller_score}/100\n商品匹配度: {matching_score}/100\n引流风险: {'是' if is_lure else '否'}"
                            }
                        },
                        {
                            "tag": "action",
                            "actions": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "查看详情"
                                    },
                                    "url": share_url,
                                    "type": "primary"
                                }
                            ]
                        }
                    ]
                }
            }
            image_infos = json.loads(item_info.image_infos)
            # 遍历 item_detail.image_infos 中的图片信息，添加到 elements 中
            image_key_count = 0
            for image_info in image_infos[:1]:
                img_key = convert_url_to_img_key(image_info.get('url'))
                message["card"]["elements"].append({
                    "tag": "img",
                    "img_key": img_key,
                    "alt": {
                        "tag": "plain_text",
                        "content": f'图_{image_key_count}'
                    }
                })
                image_key_count += 1
            
            # 发送请求
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info(f"成功发送通知: {title}")
                return True
            else:
                logger.info(f"发送通知失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.info(f"发送通知时出错: {str(e)}")
            return False

# 简单的控制台通知(用于测试)
def console_notify(item_info, seller_info, evaluation_result=None):
    """在控制台打印通知信息(测试用)"""
    
    logger.info(f"\n" + "="*50)
    logger.info(f"【好价预警】{item_info.get('title', '未知商品')}")
    logger.info(f"价格: ¥{item_info.get('price', '0')}")
    logger.info(f"卖家: {seller_info.get('data', {}).get('module', {}).get('base', {}).get('displayName', '未知卖家')}")
    logger.info(f"商品ID: {item_info.get('itemId', '')}")
    logger.info(f"-"*50)
    logger.info(f"评估结果:")
    logger.info(f"卖家可信度: {evaluation_result.get('seller_score', 0)}/100")
    logger.info(f"商品匹配度: {evaluation_result.get('matching_score', 0)}/100")
    logger.info(f"引流风险: {'是' if evaluation_result.get('is_lure', False) else '否'}")
    logger.info(f"="*50 + "\n")
    
    return True 

import requests
import os
os.environ["no_proxy"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
def get_tenant_access_token(app_id="cli_a755d0a5f3789013", app_secret="K4HxJYI7T0iSW1NfxywS1c0dnetZTStQ"):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, headers=headers, json=data, proxies={})
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["tenant_access_token"]
    return None

def upload_image_to_feishu(image_path='/Users/versa/Downloads/b61de8fe-f5f4-4fe0-8af0-d493f4dfe33a.png', access_token=get_tenant_access_token()):
    url = "https://open.feishu.cn/open-apis/image/v4/put/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        "image_type": (None, "message"),
        "image": open(image_path, "rb")
    }
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 0:
            return data["data"]["image_key"]
    return None

def convert_url_to_img_key(url):
    # 下载图片到临时文件
    import tempfile
    import os
    
    try:
        # 获取图片内容
        response = response = requests.get(url, 
                                           stream=False, 
                                           headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}, 
                                           verify=False)
        response.raise_for_status()
        
        # 创建临时文件
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(response.content)
        temp.close()
        
        # 上传到飞书获取 image_key
        image_key = upload_image_to_feishu(temp.name)
        
        # 删除临时文件
        os.unlink(temp.name)
        
        return image_key
    except Exception as e:
        logger.info(f"转换图片URL失败: {str(e)}")
        return None