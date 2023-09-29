#  coding: utf-8 
import socketserver

import os

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8')) theirs

        sep = "\r\n"
        path = "./www"
        newline = "\n"
        reqlines = self.data.decode('utf-8').split(sep)
        firstline = reqlines[0].split()
        req_type = firstline[0]
        req_ext = firstline[1]
        # print(req_type,req_ext)
        # print(firstline)


        first = "HTTP/1.1"
        headers=""
        headers_dict = {}
        body=""

        status_code = 0
        
        if req_type!="GET":
            # print("NOT GETTING")
            first += " 405 Method Not Allowed"
            headers=""
            headers_dict = {"Content Type: ":"text/html"}
            for k,v in headers_dict.items():
                headers += (k+v)+newline
            
            response = first+newline + headers+newline + body+newline
            # print("Response;")
            # print(response)
            self.request.send(response.encode())

        else:
            # print("GETTING")
            
            testpath = path + req_ext

            if not os.path.exists(testpath) or (len(req_ext)>1 and req_ext[1]=="."):
                first += " 404 Not Found"
                response = first
                
            else:
                
                if req_ext[len(req_ext)-1]=="/":
                    first += " 200 OK"
                    path += "/index.html"

                    #ADD LOCATIONreq_ext
                elif os.path.isdir(testpath):
                    first += " 301 Moved Permanently"
                    path += "/index.html"
                    status_code = 301
                    
                else:
                    first += " 200 OK"
                    path = testpath
            

                
                file_type_finder= path.split(".")
                file_type = file_type_finder[len(file_type_finder)-1]

                # print(file_type_finder)
                # print(file_type)
                if file_type=="html":
                    headers_dict["Content-Type: "] = "text/html"
                elif file_type=="css":
                    headers_dict["Content-Type: "] = "text/css"
                else:
                    headers_dict["Content-Type: "] = "text/plain"

                for k,v in headers_dict.items():
                    headers += (k+v)+newline
                response = first+newline + headers+newline
                if status_code == 301:
                    response += "Location: /index.html\n"

                file = open(path,'r')
                
                # print("Path was;\n")
                # print(path,newline)
                lines = file.readlines()
                for line in lines:
                    response += line
                response+=newline


            # print("Response; \n")
            # print(response)
            self.request.sendall((response).encode())

        # self.request.sendall(bytearray("OK",'utf-8')) 



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()






##REFERENCES##
#https://www.python-engineer.com/posts/check-if-file-exists/