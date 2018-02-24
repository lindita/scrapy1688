import numpy as np
import matplotlib.pyplot as plt  
from PIL import Image
import urllib
import random  
import os
import re   
import io


# 验证码中的字符, 就不用汉字了  
number = ['0','1','2','3','4','5','6','7','8','9']  
alphabet = []  
ALPHABET = []  
# 验证码一般都无视大小写；验证码长度4个字符  
def random_captcha_text(char_set=number+alphabet+ALPHABET, captcha_size=6):  
    captcha_text = []  
    for i in range(captcha_size):  
        c = random.choice(char_set)  
        captcha_text.append(c)  
    return captcha_text  
   
# 生成字符对应的验证码  
def gen_captcha_text_and_image():  

	captcha_text = random_captcha_text()  
	captcha_text = ''.join(captcha_text)  
	captcha = urllib.request.urlopen('http://192.168.10.8/Captcha/demo/number.php?p='+captcha_text)
	

	captcha_image = Image.open(captcha)  
	captcha_image = np.array(captcha_image)
	#cv2.imwrite('./file1/'+captcha_text + '.jpg',captcha_image)
	return captcha_text, captcha_image 



#根据图片的地址，下载图片并保存在本地   
def getAndSaveImg(imgUrl,text):  
    if( len(imgUrl)!= 0 ):  
        fileName = './file1/'+text + '.jpg' 
        urllib.request.urlretrieve(imgUrl,fileName)  
   
if __name__ == '__main__':  
	#gen_captcha_text_and_image()
	# 测试  
	text, image = gen_captcha_text_and_image()
	for i in range(100):
		captcha_text = str(i)  
		captcha_text = ''.join(captcha_text) 
		iurl = 'http://192.168.10.8/Captcha/demo/number.php?p='+captcha_text
		iurl = 'https://pin.aliyun.com/get_img?sessionid=2a5d767443719110c4d1a46275b3551b&identity=sm-laputa&type=number'
		getAndSaveImg(iurl,captcha_text)
	#cv2.imwrite('./file1/'+text + '.jpg',image)
	#print(image.shape)
	#print(text)
	#plt.imshow(image)  
	#plt.show() 




	#url = 'http://img5.iqilu.com/c/u/2015/0708/1436362650452.jpg'
	#file = urllib.request.urlopen(url)
	#tmpIm = io.StringIO(file.read())
	#img = Image.open(file)
	#img.show() 