import os
import time
import json
import requests
from PIL import Image
from datetime import datetime
from filter_by_keyword import filter_by_keyword_lastest
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from seleniumwire import webdriver

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

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
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
    driver = webdriver.Chrome(options=chrome_options,
                                       seleniumwire_options=seleniumwire_options,
                                       service=service)
    # driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    # 'source': '''
    #     Object.defineProperty(navigator, 'webdriver', {
    #         get: () => undefined
    #     });
    # '''
    # })
    return driver

def login_with_qr():
    driver = setup_driver()
    driver.get('https://www.goofish.com/')
    ActionChains(driver).move_by_offset(100, 100).perform()  # 模拟鼠标移动
    load_persistent_cookies(driver)

    # # 刷新页面以应用 cookies
    driver.refresh()
    time.sleep(3)
    # for request in driver.requests:
    #     print(f"URL: {request.url}, Status: {request.response.status_code if request.response else 'No response'}")
    try:
        login_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., '登录')]"))
        )
        login_button.click()
    except TimeoutException as e:
        filter_by_keyword_lastest(driver, 'iPhone14Pro美版')
        return
    except NoSuchElementException as e:
        filter_by_keyword_lastest(driver, 'iPhone14Pro美版')
        return

    print('等待iframe 弹出...')
    time.sleep(5)

    # Step 4: 定位 iframe 并切换上下文
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    quick_enter_button = None
    if iframes:
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                quick_enter_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., '快速进入')]"))
                )
                quick_enter_button.click()
                print("在 iframe 中定位到 `快速进入`按钮")
                
                driver.switch_to.default_content()

                persist_driver_cookies(driver)
                filter_by_keyword_lastest(driver, 'iPhone14Pro美版')
                break
            except Exception as e:
                print(e)
                driver.switch_to.default_content()  # 切换回主文档继续尝试下一个 iframe

    if not quick_enter_button:
        qr_code_container = None
        # 有提醒登录弹框
        if not iframes:
            # 无提醒登录弹框
            # cookie 中存储了登录态，并且网页中无需点击`快速登录`按钮，
            # 若无 iframe，尝试主文档
            # print("未找到 iframe，尝试在主文档中定位")
            # qr_code_container = WebDriverWait(driver, 15).until(
            #     EC.presence_of_element_located((By.ID, "qrcode-img"))
            # )
            # print("在主文档中定位到 <div id='qrcode-img'>")
            persist_driver_cookies(driver)
            filter_by_keyword_lastest(driver, 'iPhone14Pro美版')
            return
        else:
            print(f"找到 {len(iframes)} 个 iframe，尝试切换")
            for iframe in iframes:
                driver.switch_to.frame(iframe)
                try:
                    qr_code_container = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "qrcode-img"))
                    )
                    print("在 iframe 中定位到 <div id='qrcode-img'>")
                    break
                except:
                    driver.switch_to.default_content()  # 切换回主文档继续尝试下一个 iframe
            if not qr_code_container:
                print("未在任何 iframe 中找到 'qrcode-img'")
                driver.quit()
                exit(1)

        # Step 5: 定位 <canvas> 并截图
        canvas_element = qr_code_container.find_element(By.TAG_NAME, "canvas")
        qr_code_image_path = "qr_code.png"
        canvas_element.screenshot(qr_code_image_path)
        print("已截取 <canvas> 中的二维码图片")

        input("请在闲鱼 App 中扫描二维码完成登录，然后按回车继续...")

        persist_driver_cookies(driver)

        driver.switch_to.default_content()

        driver.quit()

        driver: webdriver = setup_driver()

        driver.get("https://www.goofish.com")  # 先访问域名以设置 cookies

        load_persistent_cookies(driver)

        # 刷新页面以应用 cookies
        driver.refresh()

        filter_by_keyword_lastest(driver, 'iPhone14Pro美版')

def persist_driver_cookies(driver):
    # Step 7: 提取 cookies
    cookies = driver.get_cookies()
    # print("已提取浏览器中的 cookies:")
    # for cookie in cookies:
    #     print(cookie)

    # Step 8: 保存 cookies 到文件
    with open("goofish_cookies.json", "w") as f:
        json.dump(cookies, f, indent=2)
    print("Cookies 已保存到 goofish_cookies.json")

def load_persistent_cookies(driver):
     if not os.path.exists('goofish_cookies.json'):
         return
     with open("goofish_cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            if cookie['domain'] == '.goofish.com':
                driver.add_cookie(cookie)
                print("已加载保存的 cookies")
            else:
                print(f"domain not correct: {cookie['domain']}")

if __name__ == '__main__':
    try:
        login_with_qr()
    except Exception as e:
        print(e)
        pass