import os, sys
import datetime
import time
import collections
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json 
from json import loads
from time import sleep
from json import dumps
from _thread import *
import threading

def login_authenticate():
	topic_login = "login"
	consumer = KafkaConsumer(topic_login,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

	for message in consumer:
		message = message.value
		print(message)
		res = {
			"uid":message['uid'],
			"ack":"ok"
		}
		res=dict(res)
		#producer.flush()
		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send("login_ack", json.dumps(res).encode('utf-8')) 
		producer.flush()

def register_user():
	topic_register = "register"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		message = message.value
		print(message)
		res = {
			"uid":message['uid'],
			"ack":"ok"
		}
		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send("register_ack", json.dumps(res).encode('utf-8'))
		producer.flush()


def main():
	t1 = threading.Thread(target=login_authenticate)
	t2 = threading.Thread(target=register_user)
	t1.start()
	t2.start()
	t1.join()
	t2.join()
	print("Done!")

if __name__ == '__main__':
	main()