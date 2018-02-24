import prec
#获取 sess
output,sess = prec.load_model()

imgUrl = 

#根据图片的地址，下载图片并保存在本地   
def getAndSaveImg(imgUrl):  
    if( len(imgUrl)!= 0 ):  
        fileName = './capt/download.jpg' 
        urllib.request.urlretrieve(imgUrl,fileName) 
		sleep(1)

getAndSaveImg(imgUrl)
r = prec.use_model('./capt/download.jpg',output,sess)
print(r)