from flask import Flask, jsonify, render_template,request,redirect,url_for # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
import os
from collections import deque
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind
from opentelemetry import metrics

import logging

import requests
from random import randrange

from opentelemetry.metrics import get_meter_provider

# Acceso a tracer
tracer = trace.get_tracer("sample_flask.tracer") 

# Acceso al meter
meter = metrics.get_meter("sample_flask.meter")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

title = "TODO sample application with Flask and MongoDB"
heading = "TODO Reminder with Flask and MongoDB"

mongoUri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")

client = MongoClient(mongoUri) #host uri
db = client.mymongodb    #Select the database
todos = db.todo #Select the collection name

meter = get_meter_provider().get_meter("sample-flask-app", "0.1.2")

todo_counter = meter.create_up_down_counter("todo_count")
total_altas_counter = meter.create_counter("total_altas_counter")

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route("/healthz")
def health_check():
	return jsonify({"status": "ok"})

@app.route("/list")
def lists ():
		#Display the all Tasks
		todos_l = todos.find()
		a1="active"
		if randrange(10) % 2:
			response = requests.get('https://run.mocky.io/v3/b851a5c6-ab54-495a-be04-69834ae0d2a7')
			response.close()
		else:
			response = requests.get('https://run.mocky.io/v3/1cb67153-a6ac-4aae-aca6-273ed68b5d9e')
			response.close()

		return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading), 500

@app.route("/")
@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	

	return redirect(redir)

@app.route("/action", methods=['POST'])
def action ():

	# Registrar métrica
	total_altas_counter.add(1)

	with tracer.start_as_current_span("sample_flask_prueba_final") as span_prueba_flask:

		try:


			#Adding a Task
			name=request.values.get("name")
			desc=request.values.get("desc")
			date=request.values.get("date")
			pr=request.values.get("pr")
			todos.insert({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
			todo_counter.add(1)

			span_prueba_flask.add_event("Evento creado")
			span_prueba_flask.set_attributes({
				"task.name": name,
				"task.desc": desc,
				"task.pr": pr,
				"task.date": date
			})

			logger.warning(f"El evento con nombre {name}, descripcion {desc} y fecha {date} ha sido creado")

			return redirect("/")
		
		except Exception as ex:
	
			span_prueba_flask.set_status(Status(StatusCode.ERROR))
			span_prueba_flask.record_exception(ex)
		

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.remove({"_id":ObjectId(key)})
	todo_counter.add(-1)
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(key=="_id"):
		todos_l = todos.find({refer:ObjectId(key)})
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/generate-error", methods=['GET'])
def generate_error ():
	if randrange(10) % 2:
		response = requests.get('https://rufn.fmoceky.io/v3/b851a5c6-ab54-495a-be04-69834ae0d2a7')
		response.close()
	# elif randrange(10) % 2:
	# 	listf()
	elif randrange(10) % 2:
		map[x] = "e23"
		for x in range(0, 3):
			map[x] = 3
	else:
		a3 = 100/0

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5002)