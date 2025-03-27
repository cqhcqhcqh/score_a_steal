import os
import time
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from src.logger.app_logger import app_logger as logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from .filter_by_keyword import filter_by_keyword_lastest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from src.setup import load_persistent_cookies, persist_driver_cookies

os.environ["no_proxy"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

# def setup_driver():
    # chrome_options = Options()
    # chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # service = Service(executable_path='./resources/chromedriver')
    # driver = webdriver.Chrome(options=chrome_options, service=service)    
    # # 清空请求
    # del driver.requests
    # return driver

def setup_driver(headless=True):
    chrome_options = Options()
    # chrome_options.add_argument('--start-maximized')
    if not headless:
        chrome_options.add_argument('--headless')  # Enable headless mode
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--no-proxy-server")
    # 禁用缓存和优化，确保请求可见
    # chrome_options.add_argument("--disable-cache")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_option.add_argument("--proxy-bypass-list=*")
    
    service = Service(executable_path='./resources/chromedriver')
    seleniumwire_options = {
        # 'disable_encoding': True,  # 避免编码干扰
        'verify_ssl': False,       # 忽略 SSL 验证问题
    }
    
    driver = webdriver.Chrome(
        options=chrome_options,
        seleniumwire_options=seleniumwire_options,
        service=service
    )
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    return driver

def login_with_qr(keyword=None, expected_price=None, in_days=2, feishu_webhook=None, headless=True):
    """
    二维码登录并自动搜索
    keyword: 搜索关键词，例如'iPhone14Pro美版'
    expected_price: 期望价格，例如5000
    feishu_webhook: 飞书机器人Webhook地址
    """
    driver = setup_driver(headless)
    driver.get('https://www.goofish.com/')
    ActionChains(driver).move_by_offset(100, 100).perform()  # 模拟鼠标移动
    load_persistent_cookies(driver)

    # 刷新页面以应用 cookies
    driver.refresh()
    time.sleep(3)
    # for request in driver.requests:
    #     logger.info(f"URL: {request.url}, Status: {request.response.status_code if request.response else 'No response'}")
    try:
        login_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., '登录')]"))
        )
        login_button.click()
    except TimeoutException as e:
        if keyword:
            filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)
        return
    except NoSuchElementException as e:
        if keyword:
            filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)
        return

    logger.info(f'等待iframe 弹出...')
    time.sleep(5)

    # Step 4: 定位 iframe 并切换上下文
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    quick_enter_button = None
    if iframes:
        logger.info(f'find quick_enter_button 找到 iframes')
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            logger.info(f'find quick_enter_button switch_to frame: {iframe}')
            try:
                quick_enter_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., '快速进入')]"))
                )
                quick_enter_button.click()
                logger.info("在 iframe 中定位到 `快速进入`按钮")
                
                driver.switch_to.default_content()

                persist_driver_cookies(driver)
                if keyword:
                    filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)
                break
            except Exception as e:
                logger.info(e)
                driver.switch_to.default_content()  # 切换回主文档继续尝试下一个 iframe
    else:
        logger.info(f'find quick_enter_button 没找到 iframes')

    if not quick_enter_button:
        logger.info(f'没找到 quick_enter_button')
        qr_code_container = None
        # 有提醒登录弹框
        if not iframes:
            # 无提醒登录弹框
            # cookie 中存储了登录态，并且网页中无需点击`快速登录`按钮，
            # 若无 iframe，尝试主文档
            # logger.info("未找到 iframe，尝试在主文档中定位")
            # qr_code_container = WebDriverWait(driver, 15).until(
            #     EC.presence_of_element_located((By.ID, "qrcode-img"))
            # )
            # logger.info("在主文档中定位到 <div id='qrcode-img'>")
            persist_driver_cookies(driver)
            if keyword:
                filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)
            return
        else:
            logger.info(f"找到 {len(iframes)} 个 iframe，尝试切换")
            for iframe in iframes:
                driver.switch_to.frame(iframe)
                try:
                    qr_code_container = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "qrcode-img"))
                    )
                    logger.info("在 iframe 中定位到 <div id='qrcode-img'>")
                    break
                except:
                    driver.switch_to.default_content()  # 切换回主文档继续尝试下一个 iframe
            if not qr_code_container:
                logger.info("未在任何 iframe 中找到 'qrcode-img'")
                driver.quit()
                exit(1)

        # Step 5: 定位 <canvas> 并截图
        canvas_element = qr_code_container.find_element(By.TAG_NAME, "canvas")
        qr_code_image_path = "qr_code.png"
        canvas_element.screenshot(qr_code_image_path)
        logger.info("已截取 <canvas> 中的二维码图片")

        # input("请在闲鱼 App 中扫描二维码完成登录，然后按回车继续...")
        logger.info(f'等待扫描二维码...')
        time.sleep(15)

        keep_login_button = None
        # while not keep_login_button:
        #     try:
        #         keep_login_button = WebDriverWait(driver, 1).until(
        #             EC.element_to_be_clickable((By.XPATH, "//button[contains(., '保持')]"))
        #         )
        #         keep_login_button.click()
        #         logger.info("在 iframe 中定位到 `保持`按钮")
        #     except:
        #         logger.info(f'keep find go on button.')
        #     time.sleep(1.0)

        # while not keep_login_button:
        #     driver.switch_to.default_content()
        #     iframes = driver.find_elements(By.TAG_NAME, "iframe")
        #     if iframes:
        #         logger.info(f'find keep_login_button 找到 iframes')
        #         for iframe in iframes:
        #             driver.switch_to.frame(iframe)
        #             logger.info(f'switch_to frame: {iframe}')
        #             try:
        #                 keep_login_button = WebDriverWait(driver, 1).until(
        #                     EC.presence_of_element_located((By.XPATH, "//button[contains(., '保持')]"))
        #                 )
        #                 # 打印详细信息
        #                 logger.info("按钮是否存在:", keep_login_button is not None)
        #                 logger.info("按钮可见性:", keep_login_button.is_displayed())
        #                 logger.info("按钮启用状态:", keep_login_button.is_enabled())
        #                 logger.info("按钮位置:", keep_login_button.location)
        #                 logger.info("按钮大小:", keep_login_button.size)
        #                 logger.info("按钮 HTML:", keep_login_button.get_attribute("outerHTML"))
        #                 logger.info("当前 URL:", driver.current_url)
        #                 logger.info("当前 iframe:", driver.current_frame if hasattr(driver, 'current_frame') else "主文档")
        #                 WebDriverWait(driver, 30).until(
        #                     lambda driver: keep_login_button.is_displayed() and keep_login_button.is_enabled()
        #                 )
        #                 logger.info("按钮可见性:", keep_login_button.is_displayed())
        #                 logger.info("按钮启用状态:", keep_login_button.is_enabled())
        #                 logger.info("在 ifrafme 中定位到 `保持`按钮")
        #                 driver.execute_script("arguments[0].click();", keep_login_button)
                        
        #                 driver.switch_to.default_content()

        #                 persist_driver_cookies(driver)
        #                 if keyword:
        #                     filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)
        #                 break
        #             except Exception as e:
        #                 logger.info(e)
        #                 driver.switch_to.default_content()  # 切换回主文档继续尝试下一个 iframe
        #                 break
        #     else:
        #         logger.info(f'find keep_login_button  没找到 iframes')
        #     time.sleep(1)

        persist_driver_cookies(driver)

        driver.switch_to.default_content()

        driver.quit()

        driver: webdriver = setup_driver()

        driver.get("https://www.goofish.com")  # 先访问域名以设置 cookies

        load_persistent_cookies(driver)

        # 刷新页面以应用 cookies
        driver.refresh()

        if keyword:
            filter_by_keyword_lastest(driver, keyword, expected_price, feishu_webhook, in_days)

def start_search_with_recommendation(keyword, expected_price, in_days, feishu_webhook=None):
    """
    使用推荐系统开始搜索，提供更加直观的入口
    
    keyword: 搜索关键词，例如'iPhone 14 Pro'
    expected_price: 期望价格，例如5000
    product_type: 产品类型，例如'iPhone'
    feishu_webhook: 飞书通知Webhook地址，不提供则使用控制台输出
    """
    logger.info(f"开始搜索: {keyword}, 期望价格: {expected_price}, 搜索时间范围: {in_days} 天")
    login_with_qr(keyword, expected_price, in_days, feishu_webhook)

if __name__ == '__main__':
    try:
        # 两种使用方式：
        # 1. 仅登录，不带参数
        # login_with_qr()
        
        # 2. 登录并使用推荐系统搜索
        keyword = 'iPhone 14 Pro'
        expected_price = 2500  # 元
        feishu_webhook = 'https://open.feishu.cn/open-apis/bot/v2/hook/34e8583a-82e8-4b05-a1f5-6afce6cae815'
        
        start_search_with_recommendation(keyword, expected_price, 2, feishu_webhook)
    except Exception as e:
        logger.info(e)
        pass

# if __name__ == "__main__":
#     some_function()