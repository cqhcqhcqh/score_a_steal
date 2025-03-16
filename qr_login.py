import os
import time
import json
import requests
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

os.environ["no_proxy"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
# os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

def setup_selenium_dirver():
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-proxy-server")

    service = Service(executable_path='./chromedriver')
    driver = webdriver.Chrome(options=chrome_options, 
                              service=service)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    return driver

def setup_undetected_chromedriver():
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver.execute_cdp_cmd("Network.setProxySettings", {
        "proxyType": "direct"  # 直连，不走代理
    })
    driver = uc.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    })
    return driver

def login_with_qr():
    driver: webdriver = setup_selenium_dirver()
    driver.get('https://www.goofish.com/')
    ActionChains(driver).move_by_offset(100, 100).perform()  # 模拟鼠标移动
    # with open("goofish_cookies.json", "r") as f:
    #     cookies = json.load(f)
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)
    # print("已加载保存的 cookies")

    # # 刷新页面以应用 cookies
    # driver.refresh()
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., '登录')]"))
    )
    login_button.click()
    time.sleep(5)  # 等待页面加载


    # Step 4: 定位 iframe 并切换上下文
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    qr_code_container = None
    if iframes:
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
    else:
        # 若无 iframe，尝试主文档
        print("未找到 iframe，尝试在主文档中定位")
        qr_code_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "qrcode-img"))
        )
        print("在主文档中定位到 <div id='qrcode-img'>")

    # Step 5: 定位 <canvas> 并截图
    canvas_element = qr_code_container.find_element(By.TAG_NAME, "canvas")
    qr_code_image_path = "qr_code.png"
    canvas_element.screenshot(qr_code_image_path)
    print("已截取 <canvas> 中的二维码图片")

    # time.sleep(200000)

    input("请在闲鱼 App 中扫描二维码完成登录，然后按回车继续...")

    # Step 7: 提取 cookies
    cookies = driver.get_cookies()
    print("已提取浏览器中的 cookies:")
    for cookie in cookies:
        print(cookie)

    # Step 8: 保存 cookies 到文件
    with open("goofish_cookies.json", "w") as f:
        json.dump(cookies, f, indent=2)
    print("Cookies 已保存到 goofish_cookies.json")

    driver.switch_to.default_content()

    driver.quit()

    driver: webdriver = setup_selenium_dirver()

    driver.get("https://www.goofish.com")  # 先访问域名以设置 cookies

# 加载保存的 cookies
    with open("goofish_cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    print("已加载保存的 cookies")

    # 刷新页面以应用 cookies
    driver.refresh()
    # WebDriverWait(driver, 10)
    time.sleep(200000)
login_with_qr()