#coding=utf-8
from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pandas as pd
from PIL import Image
import time
import sys
import os,os.path,datetime
import urllib
import shutil
import prec
import analyze
import mysql
import json


#os.environ["CUDA_VISIBLE_DEVICES"]=""

output,sess = prec.load_model()

#初始化 browser
#path = "./chromedriver"
#chrome_opt = webdriver.ChromeOptions()
##prefs={"profile.managed_default_content_settings.images":2}
##chrome_opt.add_experimental_option("prefs",prefs)
#browser = webdriver.Chrome(path,chrome_options=chrome_opt)

#path = "./geckodriver.exe"
browser=None

#根据图片的地址，下载图片并保存在本地
def getAndSaveImg(imgUrl,fileName):
	if( len(imgUrl)!= 0 ):
		try:
			urllib.request.urlretrieve(imgUrl,fileName)
		except	Exception as Argument:
			time.sleep(2)
			getAndSaveImg(imgUrl,fileName)


#判断元素是否存在
def is_element_exist(css):
	s = browser.find_elements_by_css_selector(css_selector = css)
	if len(s) == 0:
		#print("元素未找到：",css)
		return False
	elif len(s) >= 1:
		#print("存在元素：",css)
		return True

#移动验证码
def move_nocaptcha():
	return
	action = ActionChains(browser)
	for i in range(10):
		if i == 0:
			action.click_and_hold(dragger).move_by_offset(28, 0).perform()
		else:
			print(i)
			action.move_by_offset(0, 0).perform()
		time.sleep(0.2)


def change_handle():
	handles = browser.window_handles
	for handle in handles:# 切换窗口（切换到第二个窗口）
		if handle!=browser.current_window_handle:
			browser.switch_to_window(handle)


#加载中
def check_loading_thing(timeout,onetime):
	if not is_element_exist("#desc-lazyload-container"):
		raise Exception('#dom desc-lazyload-container cant found')
	tfir = 0
	while True:
		time.sleep(onetime)
		tfir += onetime
		if not browser.find_element_by_id("desc-lazyload-container").get_attribute('innerHTML') == '加载中...':
			return True
		if tfir > timeout:
			print('timeout')
			return False
			break


#商品页面
def grap_html():
	elem = browser.find_element_by_tag_name("html")
	#action = ActionChains(browser)
	#action.move_to_element(browser.find_element_by_id("desc-lazyload-container")).perform()

	js = 'window.location.hash = "#desc-lazyload-container";';
	#js="var q=document.documentElement.scrollTop=20000;"
	browser.execute_script(js)
	time.sleep(0.2)
	ret = check_loading_thing(60,0.5)
	if not ret:
		return grap_html()
	return analyze.parse_html(elem.get_attribute('innerHTML'))





def todo_yzm(identity = 'sm-laputa'):
	time.sleep(0.3)
	imgelement = browser.find_element_by_id('checkcodeImg')  #定位验证码
	img_url = imgelement.get_attribute('src')
	values = img_url.split('?')[-1]
	sessionid = ''
	for key_value in values.split('&'):
		arr = key_value.split('=')
		if arr[0] == 'sessionid':
			sessionid = arr[1]
	urlll = 'https://pin.aliyun.com/get_img?sessionid='+sessionid+'&identity='+identity+'&type=number'


	file0 = './capt/download.jpg';
	print('开始下载验证码')
	#存储图片
	getAndSaveImg(urlll,file0)
	print('下载完成')
	#time.sleep(10)
	#预测验证码
	#time.sleep(1)
	predit = prec.use_model(file0,output,sess)
	print('预测为:',predit)
	input_yzm = predit
	browser.find_element_by_id("checkcodeInput").send_keys(input_yzm)
	time.sleep(0.3)
	browser.find_element_by_id("checkcodeInput").send_keys(Keys.ENTER)
	time.sleep(3)
	if is_element_exist('#checkcodeImg') == False:
		#frame4.save('./capt/'+input_yzm+'.png')
		file1 = './capt/success/'+input_yzm+'.jpg'
		print('验证码验证通过,保存中'+file1)
		shutil.copy(file0, file1)
		print('pass')
	else:
		file1 = './capt/fail/'+input_yzm+'.jpg'
		print('验证码失败,保存中'+file1)
		shutil.copy(file0, file1)
		todo_yzm(identity)

def grap_page():
	if is_element_exist('#mod-detail-title'):
		#正常页面
		return grap_html()
	elif is_element_exist('#checkcodeImg'):
		#验证码页面
		todo_yzm()
		return grap_page()
	else:
		#其他页面  404 或 删除
		if(browser.current_url == 'http://page.1688.com/shtml/static/wrongpage.html'):
			print('404')
		else:
			print('下架')
		return {'code':0}


def grap(id):
	path = 'https://detail.1688.com/offer/'+id+'.html'
	#js='window.location.href = "'+path+'"'
	#打开窗口 并切换handle
	#browser.execute_script(js)
	browser.get(path)
	return grap_page()


def get_1688_list(limit):
	data=pd.read_csv('./data/info.csv')
	return data


def grap_and_save_item(item_id):
	try:
		ret=grap(str(item_id))
		mysql.save(item_id,ret)
		ret=None
	except	Exception as Argument:
		print("one error",str(Argument))
		print(item_id)
		time.sleep(10)
		mysql.save_err_item(item_id,str(Argument))

		

def todo_grap():
	global browser
	browser=webdriver.Firefox()
	print('----------------------------------------------------start--------------------------------------')
	browser.get('https://login.taobao.com/member/login.jhtml?style=b2b&css_style=b2b&from=b2b&newMini2=true&full_redirect=true&redirect_url=https%3A%2F%2Flogin.1688.com%2Fmember%2Fjump.htm%3Ftarget%3Dhttps%253A%252F%252Flogin.1688.com%252Fmember%252FmarketSigninJump.htm%253FDone%253Dhttp%25253A%25252F%25252Fmember.1688.com%25252Fmember%25252Foperations%25252Fmember_operations_jump_engine.htm%25253Ftracelog%25253Dlogin%252526operSceneId%25253Dafter_pass_from_taobao_new%252526defaultTarget%25253Dhttp%2525253A%2525252F%2525252Fwork.1688.com%2525252F%2525253Ftracelog%2525253Dlogin_target_is_blank_1688&reg=http%3A%2F%2Fmember.1688.com%2Fmember%2Fjoin%2Fenterprise_join.htm%3Flead%3Dhttp%253A%252F%252Fmember.1688.com%252Fmember%252Foperations%252Fmember_operations_jump_engine.htm%253Ftracelog%253Dlogin%2526operSceneId%253Dafter_pass_from_taobao_new%2526defaultTarget%253Dhttp%25253A%25252F%25252Fwork.1688.com%25252F%25253Ftracelog%25253Dlogin_target_is_blank_1688%26leadUrl%3Dhttp%253A%252F%252Fmember.1688.com%252Fmember%252Foperations%252Fmember_operations_jump_engine.htm%253Ftracelog%253Dlogin%2526operSceneId%253Dafter_pass_from_taobao_new%2526defaultTarget%253Dhttp%25253A%25252F%25252Fwork.1688.com%25252F%25253Ftracelog%25253Dlogin_target_is_blank_1688%26tracelog%3Dlogin_s_reg')
	WebDriverWait(browser,100000000,1).until(EC.title_contains(u"买家"))
	browser.get('about:Blank')
	ij = 0
	while(True):
		ij=ij+1
		try:
			item_list =get_1688_list(30)
		except    Exception as Argument:
			print("one error", str(Argument))
			time.sleep(300)
			continue
		if(len(item_list) == 0):
			print(ij,'------none item,sleep 180 seconds----')
			time.sleep(180)
			continue
		for x in item_list.values:
			print(ij,'---',x[0],'----','请不要关浏览器')
			grap_and_save_item(x[0])
			browser.get('about:Blank?t=不要关这个页面')
			time.sleep(3)
		time.sleep(3)

if __name__ == "__main__":
	todo_grap()