# -*- coding: utf-8 -*-
# import aircv as ac
import random
# import six
import os,base64
import time, re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# from PIL import Image
# import requests
import io
from io import BytesIO
# import cv2

class qjh(object):
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        # proxy 代理 options 选项
        # chrome_option.add_argument ( r'--proxy-server=http:\\61.135.217.7:80')
        #self.driver = webdriver.Chrome(executable_path=r"F:\下载\chromedriver.exe", chrome_options=chrome_option)
        self.driver = webdriver.Remote("http://127.0.0.1:9515/wd/hub", options=chrome_option)

        self.driver.set_window_size(1440, 900)

    def core(self):
        try:
            url="https://y.qq.com/"
            
            self.driver.get(url)

            time.sleep(3)
            
            button = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable ((By.XPATH,'//*[@id="app"]/div/div[1]/div/div[2]/span/a')))
            button.click() #点击登录

            time.sleep(2)
            
            #进入登录的iframe
            self.driver.switch_to.frame('login_frame')
            self.driver.switch_to.frame('ptlogin_iframe')
            
            btn = self.driver.find_element(By.XPATH,'//*[@id="switcher_plogin"]')
            btn.click()

            txt1 = self.driver.find_element(By.ID,'u')
            txt2 = self.driver.find_element(By.ID,'p')
            txt1.send_keys("zhanghao")
            txt2.send_keys("zhanghao2")
            
            time.sleep(1)

            #登录
            self.driver.find_element(By.ID, 'login_button').click()

            #可能出现拼图
            

            #res=res[3][0]#x坐标

            #self.start_move(res)

            # page_source =  self.driver.page_source
            # print(page_source)

            #返回主框架
            self.driver.switch_to.default_content()

            time.sleep(5)
            # 保存截图
            self.driver.get_screenshot_as_file("shot01.png")

        finally:
            self.driver.quit()


    def start_move(self, distance):
        element = self.driver.find_element(By.XPATH, '//div[@class="handler handler_bg"]')
        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(element).perform()
        time.sleep(0.5)
        while distance > 0:
            if distance > 10:
                # 如果距离大于10，就让他移动快一点
                span = random.randint(10,15)
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(2, 3)
            ActionChains(self.driver).move_by_offset(span, 0).perform()
            distance -= span
            time.sleep(random.randint(10, 50) / 100)

        ActionChains(self.driver).move_by_offset(distance, 1).perform()
        ActionChains(self.driver).release(on_element=element).perform()

if __name__ == "__main__":
    h = qjh()
    h.core()





