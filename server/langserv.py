#!/usr/bin/python
import os
import sys

#server_host = "olegst.ml"
server_port = 8080

server_host = "localhost"
#server_port = 8080


virtenv = os.path.dirname(os.path.realpath(sys.argv[0])) + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    print >> sys.stderr, "failed to run " + virtualenv
    exit(-1)

from eventlet import wsgi, websocket, listen, patcher
from webapp import WebApp

"""
import MySQLdb
from eventlet.db_pool import ConnectionPool

dbpool = ConnectionPool(MySQLdb, host='localhost', user='pythontest', passwd='1111',db='pythontest')
"""

app = WebApp()        
@app.route("/")
def handler1():
    #print ("reg" + reg)
    res =  '<head><script>\n'
    res += "console.log('starting');\n"
    res += 'var socket1 = new WebSocket("ws://{}:{}/sock1");\n'.format(server_host, server_port)
    res += 'socket1.onopen = function() {console.log("opened1"); socket1.send("hello1");};\n'
    res += "</script></head>"
    return res

@app.route("/<uid>/<mode>",methods=['POST'])
def handler2(uid,mode):
    #print ("reg" + reg)
    return "{} and {} received".format(uid,mode)

@app.wsgi_subapp("/soc?*")
@websocket.WebSocketWSGI
def socket_handler1(ws):
    msg = ws.wait()
    while msg is not None:
        ws.send("re1:" + msg)
        msg = ws.wait()

"""        
@app.route("/as")
def ashandler():
    conn = dbpool.get()
    try:
        print("Blocking...");
        print conn
        print conn.cursor()
        
        
        while True:
            conn.cursor().execute("SELECT * FROM sessions;")
        print("Done")
    finally:
        dbpool.put(conn)
        
    return "OK"
"""        
wsgi.server(listen((server_host, server_port)), app)


