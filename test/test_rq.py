import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from src.logger.app_logger import app_logger as logger

def test_seleniumwire():
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service(executable_path='../resources/chromedriver')
    driver = webdriver.Chrome(options=chrome_options, service=service)    
    # 清空请求
    del driver.requests
    
    # 访问一个简单网站
    driver.get('https://www.goofish.com')
    time.sleep(5)  # 等待请求
    
    # 检查是否捕获到请求
    if not driver.requests:
        logger.info("No requests captured.")
    else:
        logger.info(f"Captured {len(driver.requests)} requests:")
        for request in driver.requests:
            logger.info(f"URL: {request.url}")
            logger.info(f"Response: {request.response.status_code if request.response else 'No response'}")
    
    driver.quit()

if __name__ == "__main__":
    test_seleniumwire()