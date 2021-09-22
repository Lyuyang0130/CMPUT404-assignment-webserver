#  coding: utf-8 
import socketserver
import os
import sys

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
# reference:https://stackoverflow.com/questions/6803505/does-my-code-prevent-directory-traversal

class MyWebServer(socketserver.BaseRequestHandler):
    def check_secure(self,file_name):
        startdir = os.path.abspath(os.curdir)
        requested_path = os.path.relpath(file_name, startdir)
        requested_path = os.path.abspath(requested_path)
        if file_name!= requested_path:
            return False
        else:
            return True

    def handle(self):
        self.data = self.request.recv(1024).strip()
        if len(self.data)==0:
            return
        root = "./www"
        #print ("Got a request of: %s\n" % self.data)
        inf1 = self.data.decode("utf-8")
        all_string = inf1.split('\n')
        method,uri,httpV = all_string[0].split(' ')
        #print(method,uri,httpV )
        #print('uri',uri)
        
        if method != 'GET': #invalid, return 405 Method not allowed
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n",'utf-8'))
        else: #check for the uri 
            #first check for the end for 301, if invlaid, return
            if (uri[-1]!='/') and ("." not in uri): #avoid .css and .index
                inf_response = "http://127.0.0.1:8080"+ uri + "/"
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\nLocation:" +inf_response+"\r\n",'utf-8'))
            else: #html and css
                if uri[-1]=='/':
                    uri += "index.html"
                
            #print('uri here is',uri)
            if not self.check_secure(uri):
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
            else:
                #check html first
                uri = root + uri
                http_header = "HTTP/1.1 200 OK\r\nContent-Type:"
                flag = 0 #indicate 404 error
                #check the suffix 
                if uri.endswith(".html"):
                    if os.path.exists(uri):
                        with open(uri,"r") as f:
                            text = f.read()
                            flag = 1
                            self.request.sendall(bytearray(http_header+"text/html; charset=utf-8\r\n\r\n" + text+"\r\n",'utf-8'))
                            f.close()

                elif uri.endswith(".css"):
                    if os.path.exists(uri):
                        with open(uri,"r") as f:
                            text = f.read()
                            flag = 1
                            self.request.sendall(bytearray(http_header+"text/css; charset=utf-8\r\n\r\n" + text+"\r\n",'utf-8'))
                            f.close()

                if flag == 0:
                    self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n",'utf-8'))
    


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
