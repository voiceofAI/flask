#ocr_recog.py
# from config import *
import json
import requests

global API_KEY
global SECRET_KEY
global AUTH_URL
global PLANT_URL

API_KEY = 'xxx'
SECRET_KEY = 'xxx'
AUTH_URL = 'https://aip.baidubce.com/oauth/2.0/token'
PLANT_URL = 'https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general'



def img2data(filepath):
	import base64
	with open(filepath,'rb') as f:
		pic1 = base64.b64encode(f.read())
	return pic1


def get_token():
	params = {
		'grant_type' :'client_credentials',
		'client_id':API_KEY,
		'client_secret':SECRET_KEY
	}
	res = requests.post(AUTH_URL, params=params)
	# print('headers',res.request.headers)
	return res


def parse_token(res):
	a_dic=json.loads(res.text)
	token=a_dic['access_token']
	# print('token=',token)
	return token


def get_res(access_token,filepath):
	headers={
		'Content-Type':
	'application/x-www-form-urlencoded'
	}
	params = {
		'access_token':access_token,
		'image':img2data(filepath)
	}
	res = requests.post(PLANT_URL, headers=headers,data=params)
	res.raise_for_status()
	return res

def parse_query(res):
	a_dic=json.loads(res.text)
	words_result=a_dic['result']
	return words_result

def recong(filepath):
	res=get_token()
	access_token=parse_token(res)
	res=get_res(access_token,filepath)
	query=parse_query(res)
	# print(query)
	return query

if __name__=='__main__':
	filepath = 'test.png'
	print(recong(filepath))