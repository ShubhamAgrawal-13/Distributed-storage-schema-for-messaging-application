from flask import Flask, render_template, url_for, request, session, redirect  
import pymongo
import os, time
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json 
from json import loads
from time import sleep
from json import dumps
import threading

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers = 'localhost:9092')
app.secret_key = 'any random string'

users = 0
users_data = {}

def user_handle(user_id):
	global users_data
	consumer = KafkaConsumer(user_id,
	     bootstrap_servers=['localhost:9092'],
	     auto_offset_reset='latest',
	     enable_auto_commit=True,
	     value_deserializer=lambda x: loads(x.decode('utf-8')))
	print("[", user_id,"]: ", "started")
	for msg in consumer:
		recv_dict = msg.value
		print("[", user_id,"]: ", recv_dict)
		msg_id = recv_dict['msgid']
		uid1 = recv_dict['uid1']
		uid2 = recv_dict['uid2']
		print("[", user_id,"]: ", recv_dict['ack'])
		if(recv_dict['ack'] == '1'):
			if uid2 not in users_data[user_id]['msg_list']:
				users_data[user_id]['msg_list'][uid2] = {}
			users_data[user_id]['msg_list'][uid2][msg_id] = {}
			users_data[user_id]['msg_list'][uid2][msg_id]['uid'] = uid1
			users_data[user_id]['msg_list'][uid2][msg_id]['time_stamp'] = recv_dict['timestamp']
			users_data[user_id]['msg_list'][uid2][msg_id]['text'] = recv_dict['text']
		else:
			if uid1 not in users_data[user_id]['msg_list']:
				users_data[user_id]['msg_list'][uid1] = {}
			users_data[user_id]['msg_list'][uid1][msg_id] = {}
			users_data[user_id]['msg_list'][uid1][msg_id]['uid'] = uid1
			users_data[user_id]['msg_list'][uid1][msg_id]['time_stamp'] = recv_dict['timestamp']
			users_data[user_id]['msg_list'][uid1][msg_id]['text'] = recv_dict['text']
		    


@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")
    

@app.route("/login",methods=["GET","POST"])
def login():
	return render_template("login.html")

@app.route("/login_check",methods=["GET","POST"])
def login_check():
	global producer, users, users_data
	if request.method=="POST":
		req=request.form
		req=dict(req)
		# session['uid'] = req['uid']
		uid = str(req['uid'])
		print(req)
		n = len(req)
		print(n)
		
		topic = "login"
		topic_ack = "login_ack"
		
		print(topic)
		consumer = KafkaConsumer(topic_ack,
	     bootstrap_servers=['localhost:9092'],
	     auto_offset_reset='latest',
	     # auto_offset_reset='earliest',
	     group_id=None,
	     enable_auto_commit=True,
	     value_deserializer=lambda x: loads(x.decode('utf-8')))
		print(topic_ack)
		producer.send(topic, json.dumps(req).encode('utf-8'))
		for message in consumer:
			message = message.value
			print(message)
			break
		users += 1 
		users_data[uid] = {}
		users_data[uid]['cid']=None
		users_data[uid]['user_list']=[]
		users_data[uid]['group_list']=[]
		users_data[uid]['msg_list']={}
		t1 = threading.Thread(target=user_handle, args=(uid,))
		t1.start()
		return (redirect("/dashboard/" + str(uid)))
	return (redirect("/login"))

@app.route("/register",methods=["GET","POST"])
def register():
	return render_template("register.html")

@app.route("/login_check",methods=["GET","POST"])
def register_check():
	global producer, users, users_data
	if request.method=="POST":
		req=request.form
		req=dict(req)
		# session['uid'] = req['uid']
		uid = str(req['uid'])
		print(req)
		n = len(req)
		print(n)
		
		topic = "register"
		topic_ack = "register_ack"

		print(topic)
		consumer = KafkaConsumer(topic_ack,
	     bootstrap_servers=['localhost:9092'],
	     auto_offset_reset='latest',
	     # auto_offset_reset='earliest',
	     group_id=None,
	     enable_auto_commit=True,
	     value_deserializer=lambda x: loads(x.decode('utf-8')))
		print(topic_ack)
		producer.send(topic, json.dumps(req).encode('utf-8'))
		for message in consumer:
			message = message.value
			print(message)
			break

		users += 1 
		users_data[uid] = {}
		users_data[uid]['cid']=None
		users_data[uid]['user_list']=[]
		users_data[uid]['group_list']=[]
		users_data[uid]['msg_list']={}
		t1 = threading.Thread(target=user_handle, args=(uid,))
		t1.start()
		return (redirect("/dashboard/" + str(uid)))
	return (redirect("/register"))


@app.route("/dashboard/<string:user_id>",methods=["GET","POST"])
def dashboard(user_id):
	global producer, users, users_data
	
	if user_id in users_data:
		cid = users_data[user_id]['cid']
		if cid in users_data[user_id]['msg_list']:
			data4 = dict(sorted(users_data[user_id]['msg_list'][cid].items(), key = lambda kv:(kv[1]['time_stamp'], kv[0])))
			return render_template("dashboard.html", uid=user_id, users=users_data[user_id]['user_list'], groups=users_data[user_id]['group_list'], msgs=data4, cid=users_data[user_id]['cid']) 
		else:
			return render_template("dashboard.html", uid=user_id, users=users_data[user_id]['user_list'], groups=users_data[user_id]['group_list'], msgs={}, cid=users_data[user_id]['cid']) 
	return (redirect("/home"))


@app.route("/logout/<string:user_id>",methods=["POST"])
def logout(user_id):
	global users_data, users
	users -= 1
	users_data.pop(user_id)
	return (redirect("/"))


@app.route("/fetch_users/<string:user_id>", methods=['POST'])
def fetch_users(user_id):
	global producer, users, users_data
	print('fetch users')
	file = open('mappings/user.txt', 'r')
	data = file.read().splitlines()
	file.close()
	# print(data)
	# print(users_data)
	users_data[user_id]['user_list'] = data
	return (redirect("/dashboard/" + str(user_id)))



@app.route("/fetch_groups/<string:user_id>", methods=['POST'])
def fetch_groups(user_id):
	global producer, users, users_data
	print('fetch groups')
	file = open('mappings/group.txt', 'r')
	data = file.read().splitlines()
	file.close()
	# print(data)
	users_data[user_id]['group_list'] = data
	return (redirect("/dashboard/" + str(user_id)))




@app.route("/update_cid/<string:user_id>/<string:chat_id>", methods=['GET', 'POST'])
def update_cid(user_id, chat_id):
	global producer, users, users_data
	print("[update_cid] : ", user_id, chat_id)
	users_data[user_id]['cid'] = chat_id
	return (redirect("/dashboard/" + str(user_id)))



@app.route("/send/<string:user_id>", methods=['GET', 'POST'])
def send(user_id):
	global producer, users, users_data, msg_count
	#print(users_data)
	chat_id = users_data[user_id]['cid']
	print("[send] : ", user_id, chat_id)
	if request.method=="POST":
		req=request.form
		req=dict(req)
		print("[send] : ", req)
		file_name = ""
		topic1 = "loadbalancer"
		dict_send={'op_type':"send",'uid1':user_id,'uid2':chat_id,'msg':req['typed_msg']}
		producer.send(topic1, json.dumps(dict_send).encode('utf-8'))

	return (redirect("/dashboard/" + str(user_id)))



if __name__ == "__main__":
    app.run(debug=True, threaded=True)