import requests
import time
from PIL import Image
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
def setup_driver():
    chrome_option = Options()
    chrome_option.add_argument('--start-maximized')
    chrome_option.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
    chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_option.binary_location = "/Volumes/MacMiniM2/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    service = Service(executable_path='/Volumes/MacMiniM2/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(options=chrome_option, 
                              service=service)
    return driver

def login_with_qr():
    driver: webdriver = setup_driver()
    driver.get('https://www.goofish.com/')

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

    WebDriverWait(driver, 10)
    time.sleep(120)
login_with_qr()