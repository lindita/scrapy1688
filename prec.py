#coding:utf-8
from gen_captcha import gen_captcha_text_and_image
from gen_captcha import number
from gen_captcha import alphabet
from gen_captcha import ALPHABET

#coding:utf-8
import shutil
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片
import numpy as np


import numpy as np
import tensorflow as tf
import os




#text, image = gen_captcha_text_and_image()
#print("验证码图像channel:", image.shape)  # (60, 160, 3)
# 图像大小
IMAGE_HEIGHT = 30
IMAGE_WIDTH = 100
MAX_CAPTCHA = 6
#print("验证码文本最长字符数", MAX_CAPTCHA)   # 验证码最长4字符; 我全部固定为4,可以不固定. 如果验证码长度小于4，用'_'补齐




# 把彩色图像转为灰度图像（色彩对识别验证码没有什么用）
def convert2gray(img):
	if len(img.shape) > 2:
		gray = np.mean(img, -1)
		# 上面的转法较快，正规转法如下
		# r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
		# gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
		return gray
	else:
		return img

"""
cnn在图像大小是2的倍数时性能最高, 如果你用的图像大小不是2的倍数，可以在图像边缘补无用像素。
np.pad(image【,((2,3),(2,2)), 'constant', constant_values=(255,))  # 在图像上补2行，下补3行，左补2行，右补2行
"""

# 文本转向量
char_set = number + alphabet + ALPHABET + ['_']  # 如果验证码长度小于4, '_'用来补齐


CHAR_SET_LEN = len(char_set)
def text2vec(text):
	text_len = len(text)
	if text_len > MAX_CAPTCHA:
		raise ValueError('验证码最长4个字符')

	vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN) #生成一个默认为0的向量
	def char2pos(c):
		if c =='_':
			k = 62
			return k
		k = ord(c)-48
		if k > 9:
			k = ord(c) - 55
			if k > 35:
				k = ord(c) - 61
				if k > 61:
					raise ValueError('No Map')
		return k
	for i, c in enumerate(text):
		idx = i * CHAR_SET_LEN + char2pos(c)
		vector[idx] = 1
	return vector
# 向量转回文本
def vec2text(vec):
	char_pos = vec.nonzero()[0]
	text=[]
	for i, c in enumerate(char_pos):
		char_at_pos = i #c/63
		char_idx = c % CHAR_SET_LEN
		if char_idx < 10:
			char_code = char_idx + ord('0')
		elif char_idx <36:
			char_code = char_idx - 10 + ord('A')
		elif char_idx < 62:
			char_code = char_idx-  36 + ord('a')
		elif char_idx == 62:
			char_code = ord('_')
		else:
			raise ValueError('error')
		text.append(chr(char_code))
	return "".join(text)

"""
#向量（大小MAX_CAPTCHA*CHAR_SET_LEN）用0,1编码 每63个编码一个字符，这样顺利有，字符也有
vec = text2vec("F5Sd")
text = vec2text(vec)
print(text)  # F5Sd
vec = text2vec("SFd5")
text = vec2text(vec)
print(text)  # SFd5
"""



# 生成一个训练batchv  一个批次为 默认128 张图片 转换为向量
def get_next_batch(batch_size=128):
	batch_x = np.zeros([batch_size, IMAGE_HEIGHT*IMAGE_WIDTH])
	batch_y = np.zeros([batch_size, MAX_CAPTCHA*CHAR_SET_LEN])


	for i in range(batch_size):
		#获取图片，并灰度转换
		text, image = gen_captcha_text_and_image()
		image = convert2gray(image)

		# flatten 图片一维化 以及对应的文字内容也一维化，形成一个128行每行一个图片及对应文本
		batch_x[i,:] = image.flatten() / 255 # (image.flatten()-128)/128  mean为0
		batch_y[i,:] = text2vec(text)

	return batch_x, batch_y

####################################################################

# 申请三个占位符
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT*IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA*CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32) # dropout

# 定义CNN
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
	x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

	#w_c1_alpha = np.sqrt(2.0/(IMAGE_HEIGHT*IMAGE_WIDTH)) #
	#w_c2_alpha = np.sqrt(2.0/(3*3*32))
	#w_c3_alpha = np.sqrt(2.0/(3*3*64))
	#w_d1_alpha = np.sqrt(2.0/(8*32*64))
	#out_alpha = np.sqrt(2.0/1024)

	# 3 conv layer # 3 个 转换层
	w_c1 = tf.Variable(w_alpha*tf.random_normal([3, 3, 1, 32]))
	b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))
	conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
	conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv1 = tf.nn.dropout(conv1, keep_prob)

	w_c2 = tf.Variable(w_alpha*tf.random_normal([3, 3, 32, 64]))
	b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
	conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
	conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv2 = tf.nn.dropout(conv2, keep_prob)

	w_c3 = tf.Variable(w_alpha*tf.random_normal([3, 3, 64, 64]))
	b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
	conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
	conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
	conv3 = tf.nn.dropout(conv3, keep_prob)

	# Fully connected layer  # 最后连接层
	w_d = tf.Variable(w_alpha*tf.random_normal([4*13*64, 1024]))
	#w_d = tf.Variable(w_alpha*tf.random_normal([8*20*64, 1024]))
	b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
	dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
	dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
	dense = tf.nn.dropout(dense, keep_prob)

	# 输出层
	w_out = tf.Variable(w_alpha*tf.random_normal([1024, MAX_CAPTCHA*CHAR_SET_LEN]))
	b_out = tf.Variable(b_alpha*tf.random_normal([MAX_CAPTCHA*CHAR_SET_LEN]))
	out = tf.add(tf.matmul(dense, w_out), b_out)
	#out = tf.nn.softmax(out)
	return out


def crack_captcha(captcha_image):
	output = crack_captcha_cnn()
	saver = tf.train.Saver()
	sess = tf.Session();
	#with tf.Session() as sess:
	saver.restore(sess, tf.train.latest_checkpoint('./model1'))
	predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
	text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})
	#print(text_list)
	#exit()
	text = text_list[0].tolist()
	vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
	i = 0
	for n in text:
			vector[i*CHAR_SET_LEN + n] = 1
			i += 1
	return vec2text(vector)

def crack_captcha1():
	output = crack_captcha_cnn()
	saver = tf.train.Saver()
	sess = tf.Session();
	#with tf.Session() as sess:
	saver.restore(sess, tf.train.latest_checkpoint('./model1'))
	for ii in range(100):
		file1 = './file1/'+str(ii)+'.jpg'
		image = mpimg.imread('./file1/'+str(ii)+'.jpg')
		image = convert2gray(image) #生成一张新图
		captcha_image = image.flatten() / 255 # 将图片一维化
		predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
		text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})
		#print(text_list)
		#exit()
		text = text_list[0].tolist()
		vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
		i = 0
		for n in text:
				vector[i*CHAR_SET_LEN + n] = 1
				i += 1
		print(str(ii)+' is :',vec2text(vector))
		file2 = './file2/'+vec2text(vector)+'.jpg'
		shutil.copy(file1, file2)



def load_model():
	output = crack_captcha_cnn()
	saver = tf.train.Saver()
	#sess = tf.Session();
	sess = tf.Session(config=tf.ConfigProto(device_count={'gpu':0}))
	#with tf.Session() as sess:
	saver.restore(sess, tf.train.latest_checkpoint('./model'))
	# print(2)
	# exit()
	return output,sess

def use_model(file_name,output,sess):
	captcha_image = mpimg.imread(file_name)
	captcha_image = convert2gray(captcha_image) #生成一张新图
	captcha_image = captcha_image.flatten() / 255 # 将图片一维化
	predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)
	text_list = sess.run(predict, feed_dict={X: [captcha_image], keep_prob: 1})
	#print(text_list)
	#exit()
	text = text_list[0].tolist()
	vector = np.zeros(MAX_CAPTCHA*CHAR_SET_LEN)
	i = 0
	for n in text:
			vector[i*CHAR_SET_LEN + n] = 1
			i += 1
	return vec2text(vector)

def get_one(file_name):
	image = mpimg.imread(file_name)
	image = convert2gray(image) #生成一张新图
	image = image.flatten() / 255 # 将图片一维化
	predict_text = crack_captcha(image) #导入模型识别
	print("预测: {}".format(predict_text))


if __name__ == '__main__':
	captcha = urllib.request.urlopen('http://192.168.10.8/Captcha/demo/number.php?p='+captcha_text)
	captcha_image = Image.open(captcha)
	#get_one('./file1/1.jpg')
	#crack_captcha1()
