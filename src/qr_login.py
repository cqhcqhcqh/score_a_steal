import os
import time
import random
from selenium import webdriver
from src.model.queryParam import QueryModelFactory, QueryModel
# from seleniumwire import webdriver
from fake_useragent import UserAgent
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
    ua = UserAgent()
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
        # seleniumwire_options=seleniumwire_options,
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

def login_with_qr(queryParams, headless=True):
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
    # time.sleep(3)
    # for request in driver.requests:
    #     logger.info(f"URL: {request.url}, Status: {request.response.status_code if request.response else 'No response'}")
    try:
        login_button = WebDriverWait(driver, 5, poll_frequency=1.0).until(
            lambda driver: (
                logger.info(f'find `登录按钮`....'),
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., '登录')]"))(driver)
            )[1]
        )
        logger.info(f'`登录按钮`已经找到'),
        login_button.click()
    except TimeoutException as e:
        if queryParams:
            logger.info(f'没找到`登录按钮`，已经是登录态')
            filter_by_keyword_lastest(driver, queryParams)
        return
    except NoSuchElementException as e:
        if queryParams:
            logger.info(f'没找到`登录按钮`，已经是登录态')
            filter_by_keyword_lastest(driver, queryParams)
        return

    logger.info(f'等待iframe 弹出...')
    time.sleep(random.uniform(2, 4))

    # Step 4: 定位 iframe 并切换上下文
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    quick_enter_button = None
    if iframes:
        logger.info(f'find quick_enter_button 找到 iframes')
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            # logger.info(f'find quick_enter_button switch_to frame: {iframe}')
            try:
                quick_enter_button = WebDriverWait(driver, 3, poll_frequency=1.0).until(
                    lambda driver: (
                        logger.info(f'正在查找`快速进入`按钮'),
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., '快速进入')]"))(driver)
                    )[1]
                )
                quick_enter_button.click()
                logger.info("在 iframe 中定位到 `快速进入`按钮")
                
                driver.switch_to.default_content()

                persist_driver_cookies(driver)
                if queryParams:
                    filter_by_keyword_lastest(driver, queryParams)
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
            if queryParams:
                filter_by_keyword_lastest(driver, queryParams)
            return
        else:
            logger.info(f"找到 {len(iframes)} 个 iframe，尝试切换")
            for iframe in iframes:
                driver.switch_to.frame(iframe)
                try:
                    qr_code_container = WebDriverWait(driver, 5, poll_frequency=1.0).until(
                        lambda driver: (
                            logger.info(f'正在查找`二维码`'),
                            EC.presence_of_element_located((By.ID, "qrcode-img"))(driver)
                        )[1]
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

        # driver.switch_to.default_content()
        # input("请在闲鱼 App 中扫描二维码完成登录，然后按回车继续...")
        # click_keep_button(driver)
        # logger.info(f'等待扫描二维码...')

        # time.sleep(15)
        
        # source_page = driver.page_source
        # with open('./page_source.html', 'w+') as f:
        #     f.write(source_page)

        # 查找所有 "保持" 按钮
        buttons = driver.find_elements(By.XPATH, '//button[text()="保持"]')
        logger.info(f"找到 {len(buttons)} 个 '保持' 按钮")

        idx_found = None
        # 如果没有找到按钮，提前退出
        if not buttons:
            logger.info("未找到任何 '保持' 按钮，检查页面状态")
        else:
            # 遍历所有按钮，尝试找到可点击的那个
            for idx, button in enumerate(buttons):
                logger.info(f"\n检查按钮 {idx + 1}: {button.get_attribute('outerHTML')}")

                # 检查可见性和启用状态
                is_displayed = button.is_displayed()
                is_enabled = button.is_enabled()
                logger.info(f"按钮 {idx + 1} - 可见: {is_displayed}, 启用: {is_enabled}")
                if is_enabled:
                    idx_found = idx + 1

        keep_login_button = None
        while not keep_login_button:
            try:
                keep_login_button = WebDriverWait(driver, 1, poll_frequency=1.0).until(
                    lambda driver: (
                        logger.info(f'正在查找`保持`按钮'),
                        EC.element_to_be_clickable((By.XPATH, f'(//button[text()="保持"])[{idx_found}]'))(driver)
                    )[1]
                )
                keep_login_button.click()
                logger.info("在 iframe 中定位到 `保持`按钮")
            except:
                logger.info(f'keep find go on button.')
            time.sleep(2.0)

        persist_driver_cookies(driver)

        driver.switch_to.default_content()

        if queryParams:
            filter_by_keyword_lastest(driver, queryParams)

def start_search_with_recommendation(queryParams: QueryModel):
    """
    使用推荐系统开始搜索，提供更加直观的入口
    
    keyword: 搜索关键词，例如'iPhone 14 Pro'
    expected_price: 期望价格，例如5000
    product_type: 产品类型，例如'iPhone'
    feishu_webhook: 飞书通知Webhook地址，不提供则使用控制台输出
    """
    logger.info(f"开始搜索: {queryParams.keyword}, 期望价格: {queryParams.expected_price}, 搜索时间范围: {queryParams.within_days} 天")
    login_with_qr(queryParams)

if __name__ == '__main__':
    try:
        # 两种使用方式：
        # 1. 仅登录，不带参数
        # login_with_qr()
        
        # 2. 登录并使用推荐系统搜索
        start_search_with_recommendation(QueryModelFactory.stealiPhonePro256())
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.info(e)
        pass

# if __name__ == "__main__":
#     some_function()