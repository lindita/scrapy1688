#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
import json
import datetime
import mysql
import func

def innerHTML(element):
    return element.decode_contents(formatter="html")

def parse_html(html):
	if html == '':
		return {'code':0}
	result = {}
	soup = BeautifulSoup(html,'lxml')
	if not soup.select('#mod-detail-title > .d-title'):
		raise Exception('title error')
	result["title"] = str(soup.select('#mod-detail-title > .d-title')[0].string)
	if not soup.select('.bargain-number > a > em'):
		raise Exception('sales error')
	result["success_num"] = str(soup.select('.bargain-number > a > em')[0].string)
	result["comment_num"] = str(soup.select('.satisfaction-number > a > em')[0].string)
	result["imgs"] = []
	result["price"] = []
	result["objleading"] = {}
	result["objsku"] = {}

	shtml = False
	stip = soup.select('a.name')
	for tip in stip:
		if tip.get('data-tracelog') == 'wp_widget_supplierinfo_compname':
			shtml = tip
			break

	if shtml:
		seller_name=str(shtml.string)
		seller_url=shtml.get('href')
		seller_url=seller_url.split('?')[0]
		seller={'seller_name':seller_name,'seller_url':seller_url}
	else:
		seller = {'seller_name': '', 'seller_url': ''}

	for child in soup.select('.nav-tabs > li'):
		result["imgs"].append(json.loads(child.get('data-imgs'))['original'])

	for child in soup.select('.price > td'):
		if child.get('data-range'):
			result["price"].append(json.loads(child.get('data-range')))
	if(len(result["price"]) == 0):
		if soup.select('.price > td > .price-original-sku > .value'):
			price_value = soup.select('.price > td > .price-original-sku > .value')
			if(len(price_value) == 2):
				price = str(price_value[1].string)
			else:
				price = str(price_value[0].string)
			ebgin_value=str(soup.select('.amount > td > .value')[0].string)
			ebgin_value_split=ebgin_value.split('≥')
			if(len(ebgin_value_split) == 2):
				begin = ebgin_value_split[1]
			else:
				begin = ebgin_value
			end = ''
			result["price"].append({'begin':begin,'end':end,'price':price})
	try:
		result["imgs"][0]
	except IndexError:
		result["headurl"] = ''
	else:
		result["headurl"] = result["imgs"][0]

	result["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	if (not soup.select('.obj-leading')) or (not soup.select('.obj-sku')):
		raise Exception('sku error')
	if soup.select('.obj-leading'):
		result["objleading"]["title"] = soup.select('.obj-leading > .obj-header > .obj-title')[0].get_text()
		result["objleading"]["list"] = []
		for child in soup.select('.list-leading > li > div'):
			obj = {"name":"","img":""}
			if child.has_attr('data-unit-config'):
				obj["name"] = json.loads(child.get('data-unit-config'))['name']
			if child.has_attr('data-imgs'):
				obj["img"] = json.loads(child.get('data-imgs'))['original']
			result["objleading"]["list"].append(obj)

	if soup.select('.obj-sku'):
		result["objsku"]["title"] = soup.select('.obj-sku > .obj-header > .obj-title')[0].get_text()
		result["objsku"]["list"] = []
		for child in soup.select('.table-sku > tbody > tr'):
			obj = {}
			if child.get('data-sku-config'):
				obj["name"] = json.loads(child.get('data-sku-config'))['skuName']
				obj["store"] = json.loads(child.get('data-sku-config'))['max']
				if child.find_all('span',limit=1)[0].has_attr('data-imgs'):
					obj["img"] = json.loads(child.find_all('span',limit=1).get('data-imgs'))['original']
				else:
					obj["img"] = ""
				#obj['img'] = json.loads(child.get('data-imgs'))['original']
			result["objsku"]["list"].append(obj)

	description=innerHTML(soup.select('#desc-lazyload-container')[0])
	description = description.replace('"', "'");
	result["prop"] = ""
	if soup.select('#mod-detail-attributes'):
		lens = len(soup.select('#mod-detail-attributes')[0].find_all('td'))
		i = 0
		for child in soup.select('#mod-detail-attributes')[0].find_all('td'):
			i = i + 1
			if(i != lens):
				if(child.get('class')[0] == 'de-feature'):
					result['prop'] = result['prop'] + child.get_text() + ':'
				if(child.get('class')[0]  == 'de-value'):
					result['prop'] = result['prop'] + child.get_text() + ','
	data=todo_json(result)
	html = None
	soup = None
	return {'code':1,'data':data,'description':description,'seller':seller}



# def todo_list(html,fir):
# 	file_object = open('./a.html', 'w' ,encoding='utf-8')
# 	file_object.write(html)
# 	file_object.close( )
# 	result = []
# 	soup = BeautifulSoup(html,'lxml')
# 	pagebar = soup.select('#fui_widget_4')
#
# 	if not soup.select('#sm-offer-list > li'):
# 		return {'code':2,'result':result}
#
# 	for child in soup.select('#sm-offer-list > li'):
# 		item_id = child.get('trace-obj_value')
# 		result.append(item_id)
#
# 	if not pagebar:
# 		return {'code':2,'result':result}
# 	elif (len(result) < 60):
# 		return {'code':0}
# 	return {'code':1,'result':result}


def todo_list(html,fir):
	# file_object = open('./a.html', 'w' ,encoding='utf-8')
	# file_object.write(html)
	# file_object.close( )
	result = []
	soup = BeautifulSoup(html,'lxml')
	xx = soup.select('#fui_widget_4 > span > .fui-next')[0]
	classes = xx.get('class')
	for child in soup.select('#sm-offer-list > li'):
		item_id = child.get('trace-obj_value')
		result.append(item_id)
	if fir > 7:
		return {'code': 2,'result':result}
	#print(result)
	if ('fui-next-disabled' not in classes) and (len(result) < 60):
		print('fir--',fir,'len--',len(result),'try again')
		return {'code':0}
	if ('fui-next-disabled' in classes):
		return {'code':2,'result':result}
	return {'code':1,'result':result}


def store(data,id):
    with open('./file/'+id+'.json', 'w') as json_file:
        json_file.write(json.dumps(data))

def load():
    with open('data.json') as json_file:
        data = json.load(json_file)
        return data

def dict2flatlist(d):
	for x in d.keys():
		if type(d[x]) == dict:
			d[x]=dict2flatlist(d[x])
		else:
			d[x]=fiter_json(d[x])
	return d

def fiter_json(theString):
	if(isinstance(theString,str)):
		theString = theString.replace("\n", ""); 
		theString = theString.replace("\r", "");  
		theString = theString.replace("\r\n", "");  
		theString = theString.replace("\t", ""); 
		theString = theString.replace("\\", "")
		theString = theString.replace("'", "&acute;"); 
		theString = theString.replace('"', "&quot;"); 
	return theString

def todo_json(data):
	data=dict2flatlist(data)
	data = json.dumps(data)
	data = json.loads(data)
	return data

def store_mysql(data,id):
	mysql.save(id,data)

#分析并保存
def todo(html,id):
	if(html != ''):
		ret = parse_html(html)
		store(ret,id)
	else:
		store({'code':0},id)

def todo_mysql(html,id):
	if(html != ''):
		ret = parse_html(html)
		store_mysql(ret,id)
	else:
		store_mysql({'code':0},id)


def get_last_id():
	return mysql.get_last_id()

if __name__ == '__main__':
	id = "537610897261"
