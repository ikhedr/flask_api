# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 09:51:41 2018

@author: datta
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/<username>')
def hello(username="Datta"):
    return 'Hello there {}'.format(username)

if(__name__=='__main__'):
    app.run(debug=True)