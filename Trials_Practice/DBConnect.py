# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 22:59:06 2018

@author: datta
"""

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

#Database name
app.config['MONGO_DBNAME'] = 'tickets'

# use mlab.com to take temperory dbs
#mongodb://<dbuser>:<dbpassword>@ds241012.mlab.com:41012/DatabaseName

app.config['MONGO_URI'] = 'mongodb://datta:datta1@ds241012.mlab.com:41012/tickets'

mongo = PyMongo(app)

@app.route("/add")
def add():
    user = mongo.db.users
    user.insert([{'name':'Jaanu','language':'Spanish'}])
    return 'added user...'

@app.route('/find')
def find():
    user = mongo.db.users
    #make sure it matches something, otherwise it will give error for None Type
    cust1 = user.find_one({'name':'Jaanu'})
    return ('You Found '+ cust1['name'] + '. He knows ' + cust1['language'])

@app.route('/update')
def update():
    user = mongo.db.users
    jaanu = user.find_one({'name':'Jaanu'})
    jaanu['language'] = 'English'
    user.save(jaanu)
    return 'Updated the record'

@app.route('/delete')
def delete():
    user = mongo.db.users
    pwd = user.find_one({'pwd':'1234'})
    user.remove(pwd)
    return 'removed pwd'

if(__name__=='__main__'):
    app.run(debug=True)