//
// fabnetserver.js
// Nadya Peek 2016 peek@mit.edu
//
// purpose:
// this server listens for commands from mods.cba.mit.edu
// specifically from the module fabnetclient.js
// and uses them to run the pygestalt virtual machine "fabnet_xyaxes.py".
// you can replace fabnet_xyaxes.py with your own virtual machine.
// 
// dependencies:
// ws (npm install ws)
// pyserial (apt-get install python-serial)
// pygestalt (git clone http://github.com/nadya/pygestalt, python setup.py install)
// the folder you run this in also needs to contain 
// fabnet_xyaxes.py
// 086-005a.py
//
// usage:
// run this server with node e.g. node fabnetserver.js
// it should say
// "listening for connections from 127.0.0.1 on 1234"
// then you can use the a module in mods.cba.mit.edu that connects to this server
// such as the fabnet module. add it to the mods environment and press
// the button "connect to server"
// you should then be able to send paths to the server.
//
//

var server_port = '1234'
var client_address = '127.0.0.1'

console.log("listening for connections from "+client_address+" on "+server_port)

var server = {}

var WebSocketServer = require('ws').Server
wss = new WebSocketServer({port:server_port})

function worker(ws,arg) {
   var child_process = require('child_process')
   console.log("python dummy.py '"+arg+"'")
   // replace fabnet_xyaxes with your virtual machine here
   child_process.exec("python dummy.py '"+arg+"'",function(err,stdout,stderr) {
      ws.send(stdout)
      })
   }

server.worker = worker;

wss.on('connection',function(ws) {
   if (ws._socket.remoteAddress != client_address) {
      console.log("error: client address doesn't match")
      return
      }
   ws.on('message',function(msg) {
      //console.log('message: '+msg);
      server.worker(ws,msg);
      })
   })
