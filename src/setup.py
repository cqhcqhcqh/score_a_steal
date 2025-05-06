import os
import json
# from seleniumwire import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from src.logger.app_logger import app_logger as logger

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--start-maximized')
    # chrome_options.add_argument('--headless')  # Enable headless mode
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
        'disable_encoding': True,  # 避免编码干扰
        'verify_ssl': False,       # 忽略 SSL 验证问题
    }
    
    driver = webdriver.Chrome(
        options=chrome_options,
        # seleniumwire_options=seleniumwire_options,
        service=service
    )
    
    # driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    #     'source': '''
    #         Object.defineProperty(navigator, 'webdriver', {
    #             get: () => undefined
    #         });
    #     '''
    # })
    return driver

def persist_driver_cookies(driver):
    # Step 7: 提取 cookies
    cookies = driver.get_cookies()
    # logger.info("已提取浏览器中的 cookies:")
    # for cookie in cookies:
    #     logger.info(cookie)

    # Step 8: 保存 cookies 到文件
    with open("goofish_cookies.json", "w") as f:
        json.dump(cookies, f, indent=2)
    logger.info("Cookies 已保存到 goofish_cookies.json")

def load_persistent_cookies(driver):
    if not os.path.exists('goofish_cookies.json'):
        return
    with open("goofish_cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            if cookie['domain'] == '.goofish.com':
                driver.add_cookie(cookie)
            else:
                logger.info(f"domain not correct: {cookie['domain']}")
        logger.info("已加载保存的 cookies")