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
from PIL import Image
# import requests
import io
from io import BytesIO
import cv2

class qq(object):
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        chrome_option.add_argument('User-Agent=' + UserAgent)
        # proxy 代理 options 选项
                
        #代理IP池
        # proxy_arr = [
        #     '--proxy-server=http://111.3.118.247:30001',
        #     '--proxy-server=http://183.247.211.50:30001',
        #     '--proxy-server=http://122.9.101.6:8888',
        # ]
        # proxy = random.choice(proxy_arr)  # 随机选择一个代理
        # print(proxy) #如果某个代理访问失败,可从proxy_arr中去除
        # chrome_option.add_argument(proxy)  # 添加代理

        #self.driver = webdriver.Chrome(executable_path=r"F:\下载\chromedriver.exe", chrome_options=chrome_option)
        self.driver = webdriver.Remote("http://127.0.0.1:9515/wd/hub", options=chrome_option)

        self.driver.set_window_size(1440, 900)

    def landpage(self):
        try:
            url="https://mail.qq.com/"
            
            self.driver.get(url)

            button = WebDriverWait(self.driver,3).until(EC.element_to_be_clickable ((By.XPATH,'//*[@id="qqLoginTab"]')))
            button.click() #点击登录

            time.sleep(2)
            
            #进入登录的iframe
            self.driver.switch_to.frame('login_frame')
            
            txt1 = self.driver.find_element(By.ID,'u')
            txt2 = self.driver.find_element(By.ID,'p')
            txt1.send_keys("zhanghao")
            time.sleep(1)
            txt2.send_keys("zhanghao2")
            time.sleep(1)

            self.driver.get_screenshot_as_file("shot01.png")

            #登录
            self.driver.find_element(By.ID, 'login_button').click()

            #出现拼图iframe
            left_1 = 1200 - 334 # 在网站中的位置
            top_1 = 200 # 在网站中的位置
            time.sleep(3)
            self.driver.get_screenshot_as_file("shot02.png")
            try:
                self.driver.switch_to.frame('tcaptcha_iframe_dy')    #进入拼图

                bg = self.driver.find_element(By.XPATH,'//*[@id="slideBg"]')
                bg.screenshot('pintu_origin.png')

                #缺口图片//*
                list_dom = self.driver.find_elements(By.XPATH,'//*[@id="tcOperation"]/div')
                for dom in list_dom:
                    if dom.get_attribute('style').count('background-image') > 0 and dom.size['width'] < 100:
                        dom.screenshot('quekou.png')
                        break

                self.driver.execute_script('arguments[0].style.display="none"',dom)    # 隐藏缺口，好给后面的拼图截图

                #拼图背景图//*[@id="slideBg"]
                bg.screenshot('pintu.png')

                self.driver.execute_script('arguments[0].style.display=""',dom)  #显示缺口

                cv2_left = self.identify_gap('pintu.png','quekou.png') #cv2匹配检查出的离背景左边边缘的距离
                print('cv2 get the left x is ',cv2_left)

                # #拖动按钮
                list_sytle = dom.get_dom_attribute("style").split(';')
                print(list_sytle)
                left_x = 0 # 拖动按钮离背景左边边缘的距离
                for name in list_sytle:
                    if name.count('left:')>0:
                        left_x = name.split(':')[1].replace('px','').replace(' ','')
                        print('left_x ',left_x)
                        break

                print(cv2_left , left_x)
                if abs(left_x) - abs(cv2_left) < 20: #可能就是没正确识别出来距离
                    #点击刷新拼图
                    return


                return    
                juli = int(cv2_left) - int(left_x)
                print(juli)
                self.start_move(juli)

            finally:
                time.sleep(1)

            # page_source =  self.driver.page_source
            # print(page_source)

            #返回主框架
            self.driver.switch_to.default_content()
        except:
            print('exception...')    
        finally:
            self.driver.quit()

    #参考资料 https://blog.csdn.net/zhangzeyuaaa/article/details/119508407    
    def identify_gap(self,bg,tp):
        '''
        bg: 背景图片
        tp: 缺口图片
        '''
        # 读取背景图片和缺口图片
        bg_img = cv2.imread(bg) # 背景图片
        tp_img = cv2.imread(tp) # 缺口图片
        
        # 识别图片边缘
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        
        # 转换图片格式
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        
        # 缺口匹配
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 寻找最优匹配
        
        # 绘制方框
        th, tw = tp_pic.shape[:2] 
        tl = max_loc # 左上角点的坐标
        br = (tl[0]+tw,tl[1]+th) # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2) # 绘制矩形
        out = 'check_cv2.png'
        cv2.imwrite(out, bg_img) # 保存在本地
        
        # 返回缺口的X坐标（背景图里面的缺口？应该是）
        return tl[0] 

    def start_move(self, distance):

        #拖动按钮
        element =  self.driver.find_element(By.XPATH,'//*[@id="tcOperation"]/div[6]')
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
            self.driver.get_screenshot_as_file("move"+distance+".png") #连拍
            time.sleep(random.randint(10, 50) / 100)

        ActionChains(self.driver).move_by_offset(distance, 1).perform()
        ActionChains(self.driver).release(on_element=element).perform()

if __name__ == "__main__":
    h = qq()
    h.landpage()





