#!/usr/bin/python
import os
import sys

server_host = "olegst.ml"
#server_host = "localhost"
server_port = 8080

virtenv = os.path.dirname(os.path.realpath(sys.argv[0])) + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    print >> sys.stderr, "failed to run " + virtualenv
    exit(-1)

from eventlet import wsgi, websocket, listen, patcher
from webapp import WebApp
#import MySQLdb
#from eventlet.db_pool import ConnectionPool
#from langapi import LangAPI

#dbpool = ConnectionPool(MySQLdb, host='localhost', user='pythontest', passwd='1111',db='pythontest')
#dbconnection = dbpool.get()

#api = LangAPI()
#api.init(dbconnection)
#api.dbcreate()

app = WebApp() 

@app.route("/")
def handler1(ctx):
    res =  '<head><script>\n'
    res += "console.log('starting');\n"
    res += 'var socket1 = new WebSocket("ws://{}:{}/sock1");\n'.format(server_host, server_port)
    res += 'socket1.onopen = function() {console.log("opened1"); socket1.send("hello1");};\n'
    res += "</script></head>"
    return res

#@app.route("/profile",methods=['POST'])
#def add_profile(ctx):
#    api.register(ctx.req_post_params.)

@app.route("/post",methods=['POST'])
def add_profile(ctx):
    for i,v in ctx.__dict__.items():
        print "{} : {}".format(i,v)
    return "OK"



@app.route("/<uid>/<mode>",methods=['POST'])
def handler2(ctx,uid,mode):
    #print ("reg" + reg)
    return "{} and {} received".format(uid,mode)

@app.wsgi_subapp("/soc?*")
@websocket.WebSocketWSGI
def socket_handler1(ws):
    msg = ws.wait()
    while msg is not None:
        ws.send("re1:" + msg)
        msg = ws.wait()


wsgi.server(listen((server_host, server_port)), app)

