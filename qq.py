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
import sys
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib import parse

class qq(object):
    def __init__(self):
        chrome_option = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        chrome_option.add_argument('User-Agent=' + user_agent)
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

        self.zhanghao = sys.argv[1]
        self.mima = sys.argv[2]

        self.api = 'http://localhost/api/v1'

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
            txt1.send_keys(self.zhanghao)
            time.sleep(1)
            txt2.send_keys(self.mima)
            time.sleep(1)

            self.driver.get_screenshot_as_file("shot01.png")

            #登录
            self.driver.find_element(By.ID, 'login_button').click()

            #出现拼图iframe
            time.sleep(3)
            self.driver.get_screenshot_as_file("shot02.png")
            self.driver.switch_to.frame('tcaptcha_iframe_dy')    #进入拼图
            self.pintu()

            # page_source =  self.driver.page_source
            # print(page_source)

            #返回主框架
            self.driver.switch_to.default_content()
        except Exception as e:
            print(e)    
            # f = open('e.html','w')
            # f.write(self.driver.page_source)
            # f.close()
            #网络波动
            urlopen(self.api + '/qq/bodong?' + parse.urlencode({
                'qq': self.zhanghao,
            }))
        finally:
            self.driver.quit()

    def pintu(self):#拼图验证，距离不对就递归调用
        time.sleep(3)

        bg = self.driver.find_element(By.XPATH,'//*[@id="slideBg"]')
        bg.screenshot('pintu_origin.png')

        #缺口图片
        list_dom = self.driver.find_elements(By.XPATH,'//*[@id="tcOperation"]/div')
        #得到缺口图片，赋给dom
        for dom in list_dom:
            if dom.get_attribute('style').count('background-image') > 0 and dom.size['width'] < 100:
                dom.screenshot('quekou.png')

                self.driver.execute_script('arguments[0].style.display="none"',dom)    # 隐藏缺口，好给后面的拼图截图
                time.sleep(1)
                bg.screenshot('pintu_bg.png') #截图

                break

        self.driver.execute_script('arguments[0].style.display=""',dom)  #显示缺口
        time.sleep(1)
        edge_left = self.identify_gap('pintu_bg.png','quekou.png') #cv2匹配检查出的离背景左边边缘的距离
        print('识别出背景图片的缺口距离边距 ',edge_left)

        # #拖动按钮
        list_sytle = dom.get_dom_attribute("style").split(';')
        print(list_sytle)
        left_x = 0 # 拖动按钮离背景左边边缘的距离
        for name in list_sytle:
            if name.count('left:')>0:
                left_x = name.split(':')[1].replace('px','').replace(' ','')
                print('拖动按钮距离边距 ',left_x)
                break

        left_x = float(left_x)    
        tuodongjuli = abs(edge_left - left_x)
        if  tuodongjuli < 20: #可能就是没正确识别出来距离
            print('刷新操作，距离 ',tuodongjuli)
             #点击刷新拼图
            self.driver.find_element(By.ID,'e_reload').click()
            #点击刷新拼图 再次 尝试拼图
            self.pintu()
            return
        else:
            print('还需要向右拖动 ',tuodongjuli)

        self.start_move(tuodongjuli)


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
            #self.driver.get_screenshot_as_file("movepng/d"+str(distance)+".png") #连拍
            time.sleep(random.randint(10, 50) / 100)
   
        ActionChains(self.driver).move_by_offset(distance, 1).perform()
        ActionChains(self.driver).release(on_element=element).perform()

        
        #查看是否有登录的反馈错误提示信息
        time.sleep(2)
        self.driver.switch_to.default_content()

        #记录此时的源代码
        f = open('after_click_login.html','w')
        f.write(self.driver.page_source)
        f.close()
        
        login_err_msg = ''
        try:
            time.sleep(1)
            self.driver.switch_to.frame('login_frame') #切换不过去iframe，说明此时已经登录成功了
            login_err_msg = ''

            #识别提示信息
            check_times = 0

            while(check_times<5): #循环查看是否有了错误提示反馈
                check_times += 1
                login_err_msg = self.driver.find_element(By.ID,'err_m').get_attribute('textContent').strip()
                if len(login_err_msg) == 0:
                    time.sleep(0.2)
                    continue
                
        except:
            login_err_msg = ''
        
        print(login_err_msg)
        #上报结果
        urlopen(self.api + '/qq/save?' + parse.urlencode({
            'qq': self.zhanghao,
            'msg': login_err_msg,
        }))

# python3 qq.py 账号 密码
if __name__ == "__main__":
    h = qq()
    print(sys.argv[1],sys.argv[2])
    h.landpage()





