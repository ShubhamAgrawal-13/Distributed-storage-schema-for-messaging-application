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
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# f = db.createCollection("user_info")
# print(f)
user_db = myclient["authentication"]
user_table = user_db["user_info"]

"""
{ User Info Table}

{
	{
		"user_id": message['uid'],
		"email": message['email'], 
		"password": message['password']
	}
}

"""

"""
{ Group Info Table }

{
	{
		"grp_id" : message['grp_id']
		"members" : {"user1":"1", "user2":"1", "user3":"1"}
	}
}
"""


group_table = user_db["group_info"]

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
		print("[login]")
		message = message.value
		query = user_table.find({"user_id": message['uid']})
		flag = 0
		for x in query:
			# print("[query : ]", x)
			if(x["password"]  == message["password"]):
				flag=1
			else:
				flag=0
			break

		# print("[message : ]", message)
		print("Login: ", message)
		res = {
			"uid":message['uid'],
			"ack":flag
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
		print("[register]")
		message = message.value
		reg_dict = { 
					"user_id": message['uid'],
					"email": message['email'], 
					"password": message['password']
				 }

		query = user_table.find({"user_id": message['uid']})
		flag=0
		# print(query)
		for x in query:
			flag+=1
		print("flag : ", flag)
		res = {
				"uid":message['uid'],
				"ack":"0"
			  }
		if(flag == 0):
			x1 = user_table.insert_one(reg_dict)
			# print(x1)
			print("Register: ", message)
			res["ack"] = "1"

		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send("register_ack", json.dumps(res).encode('utf-8'))
		producer.flush()

def fetch_users():
	topic_register = "fetch_users"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[fetch_users]")
		message = message.value
		# print(message)
		user_id = message['uid']
		user_list = {}
		query = user_table.find()
		user_list = []
		for x in query:
			# print("[query : ]", x["user_id"])
			user_list.append(x["user_id"])
		# print(user_list)
		res = {
			"ack":'2',
			"users":user_list
		}

		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send(user_id, json.dumps(res).encode('utf-8'))
		producer.flush()


def fetch_groups():
	topic_register = "fetch_groups"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[fetch_groups]")
		message = message.value
		# print(message)
		user_id = message['uid']
		group_list = []
		query = group_table.find()
		for x in query:
			# print("[query : ]", x["user_id"])
			group_list.append(x["grp_id"])
		# print(user_list)
		res = {
			"ack":'3',
			"grp_ids":group_list
		}

		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send(user_id, json.dumps(res).encode('utf-8'))
		producer.flush()


def create_grp():
	topic_register = "create_grp"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[create_grp]")
		message = message.value
		reg_dict = { 
					"grp_id": message['grp_id'],
					"members": {} 
				 }

		query = group_table.find({"grp_id": message['grp_id']})
		flag=0
		# print(query)
		for x in query:
			flag+=1
		print("flag : ", flag)
		if(flag == 0):
			x1 = group_table.insert_one(reg_dict)
			# print(x1)
			print("New Group Created : ", message['grp_id'])
		else:
			print("Already exists: ", message['grp_id'])
		time.sleep(0.5)


def join_grp():
	topic_register = "join_grp"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[join_grp]")
		message = message.value
		grp_id = message['grp_id']
		user_id = message['uid']
		query = group_table.find({"grp_id": grp_id})
		flag=0
		# print(query)
		members = {}
		for x in query:
			members = x['members']
			flag+=1
		print("flag : ", flag)
		print(members)
		if(flag == 1):
			members[user_id]='1'
			x1 = group_table.update(
					{
						 "grp_id": grp_id
					},
					{
						"$set" :
						{
							"members" : members
						}
					}
 				)
			# print(x1)
			print("Added user in : ", grp_id, " with user id : ", user_id)
		else:
			print("No group exists: ", grp_id)

		time.sleep(0.5)

def leave_grp():
	topic_register = "leave_grp"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[leave_grp]")
		message = message.value
		grp_id = message['grp_id']
		user_id = message['uid']
		query = group_table.find({"grp_id": grp_id})
		flag=0
		# print(query)
		members = {}
		for x in query:
			members = x['members']
			flag+=1
		print("flag : ", flag)
		print(members)
		if(flag == 1):	
			if user_id in members:		
				members.pop(user_id)
				x1 = group_table.update(
						{
							 "grp_id": grp_id
						},
						{
							"$set" :
							{
								"members" : members
							}
						}
	 				)
				# print(x1)
				print("Removed user in : ", grp_id, " with user id : ", user_id)
			else:
				print('No user exists in ', grp_id, ' with the given user id : ', user_id)
		else:
			print("No group exists: ", grp_id)

		time.sleep(0.5)

def show_grp():
	topic_register = "show_grp"
	consumer = KafkaConsumer(topic_register,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     # auto_offset_reset='earliest',
	 group_id=None,
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))
	for message in consumer:
		print("[show_grp]")
		message = message.value

		grp_id = message['grp_id']
		user_id = message['uid']
		query = group_table.find({"grp_id": grp_id})
		flag=0
		# print(query)
		res = {}
		res['uid'] = user_id
		res['grp_id'] = grp_id
		res['members'] = []
		res['flag'] = "group exists"
		for x in query:
			res['members'] = x['members']
			flag+=1
		print("flag : ", flag)
		print(res)

		if(flag == 0):
			res['flag'] = "group doesn't exists"
			res['members'] = []
			print("No group exists: ", grp_id)

		time.sleep(0.5)
		producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
		producer.send("show_grp_ack", json.dumps(res).encode('utf-8'))
		producer.flush()




def main():
	t1 = threading.Thread(target=login_authenticate)
	t2 = threading.Thread(target=register_user)
	t3 = threading.Thread(target=fetch_users)
	t4 = threading.Thread(target=fetch_groups)
	t5 = threading.Thread(target=create_grp)
	t6 = threading.Thread(target=join_grp)
	t7 = threading.Thread(target=leave_grp)
	t8 = threading.Thread(target=show_grp)
	t1.start()
	t2.start()
	t3.start()
	t4.start()
	t5.start()
	t6.start()
	t7.start()
	t8.start()
	
	t1.join()
	t2.join()
	t3.join()
	t4.join()
	t5.join()
	t6.join()
	t7.join()
	t8.join()
	
	print("Done!")

if __name__ == '__main__':
	main()