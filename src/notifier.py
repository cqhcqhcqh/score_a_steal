import json
import requests
from datetime import datetime

class FeiShuNotifier:
    """飞书机器人通知类"""
    
    def __init__(self, webhook_url):
        """
        初始化飞书通知器
        webhook_url: 飞书机器人的Webhook地址
        """
        self.webhook_url = webhook_url
    
    def send_deal_notification(self, item_info, seller_info, evaluation_result):
        """
        发送优质商品信息到飞书
        item_info: 商品信息
        seller_info: 卖家信息
        evaluation_result: 评估结果
        """
        try:
            # 提取商品关键信息
            title = item_info.get('title', '未知商品')
            price = item_info.get('price', '0')
            item_id = item_info.get('itemId', '')
            desc = item_info.get('description', '无描述')
            
            # 构建分享链接
            share_url = f"https://item.goofish.com/{item_id}"
            
            # 提取卖家信息
            seller_name = seller_info.get('data', {}).get('module', {}).get('base', {}).get('displayName', '未知卖家')
            
            # 提取评估结果
            seller_score = evaluation_result.get('seller_score', 0)
            matching_score = evaluation_result.get('matching_score', 0)
            is_lure = evaluation_result.get('is_lure', False)
            seller_analysis = evaluation_result.get('seller_analysis', [])
            matching_analysis = evaluation_result.get('matching_analysis', [])
            
            # 构建通知内容
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"【好价预警】{title}"
                        },
                        "template": "red" if matching_score >= 80 else "blue"
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
            
            # 发送请求
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                print(f"成功发送通知: {title}")
                return True
            else:
                print(f"发送通知失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"发送通知时出错: {str(e)}")
            return False

# 简单的控制台通知(用于测试)
def console_notify(item_info, seller_info, evaluation_result):
    """在控制台打印通知信息(测试用)"""
    
    print("\n" + "="*50)
    print(f"【好价预警】{item_info.get('title', '未知商品')}")
    print(f"价格: ¥{item_info.get('price', '0')}")
    print(f"卖家: {seller_info.get('data', {}).get('module', {}).get('base', {}).get('displayName', '未知卖家')}")
    print(f"商品ID: {item_info.get('itemId', '')}")
    print("-"*50)
    print(f"评估结果:")
    print(f"卖家可信度: {evaluation_result.get('seller_score', 0)}/100")
    print(f"商品匹配度: {evaluation_result.get('matching_score', 0)}/100")
    print(f"引流风险: {'是' if evaluation_result.get('is_lure', False) else '否'}")
    print("="*50 + "\n")
    
    return True 