import pymysql
import datetime
import json


class MysqlConnection(object):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__new__(cls, *args, **kwargs)
			cls._instance.create_connection()
		return cls._instance

	#def __init__(self):
		# Connect to the database
		#self.connection = pymysql.connect(**config)
		#if not hasattr(self._instance, 'pool'):
			#self._instance.create_connection()


	def create_connection(self):
		self.connection = pymysql.connect(host='xxx', user='xxx',
										  passwd='xxx', db='xxx', port=3306, charset='utf8')

	def get_conn(self):
		self.ping_connect()
		return self.connection

	def ping_connect(self):
		try:
			self.connection.ping()
		except:
			self.create_connection()


def get_conn():
	return MysqlConnection().get_conn()


def save(id,ret):
	with open("./file/"+str(id)+".json","w") as f:
		json.dump(ret,f)
	print("saving file","./file/"+str(id)+".json")

def save_err_item(id,msg):
	print(id,msg)



if __name__ == '__main__':
	print('xxx')