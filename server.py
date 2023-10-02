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


#Assignment 1 server implementation provided by Daniel Asimiakwini

encoding = 'utf-8'
newline = "\n"

web_root = "./www" #the www folder int he current dir
http = "HTTP/1.1 "

status_codes = {"200":"200 OK", "301":"301 Moved Permanently", "403":"403 Forbidden", "404":"404 Not Found", "405":"405 Method Not Allowed"}

headers_list=["Content-Type: ", "Content-Size: ", "Location: ", "Connection: "]
headers_default=["text/plain", "0", "", "close"]

#send reposne to user agent
def send(socket, response):
    socket.sendall(response.encode(encoding))

#add slash for path ending
def withSlash(path):
    return path+"/"

#the body of a resposne
def addBody(code, ext):
    body=""
    if code[0]=="4": #error notif for user
        file = open(ext, 'r')

    elif code[0]=="3": #change the path for the user
        exist = os.path.exists(ext+"index.html")
        if exist:
            file = open(web_root+ext+"index.html", 'r')
        else:
            return "" 
        
    else:# ez 200 ok
        file = open(web_root+ext, 'r')

    filelines = file.readlines()
    for line in filelines:
        body += line
    return body

#the header(s) of a reposne
def addHeaders(code, ext):
    headers=""
    if code=="200":
        #ONLY 0, 1 and 3
        #0
        cont_type_header = headers_list[0]
        file_type = ext.split(".")[1]
        accepted_mimes = {"html", "css"}
        if file_type in accepted_mimes:
            headers += (cont_type_header + "text/"+file_type + newline)
        else:
            headers += (cont_type_header + headers_default[0] + newline)
        
        #1
        cont_size_header = headers_list[1]
        content_bytesize = os.path.getsize(web_root+ext)
        headers += (cont_size_header + str(content_bytesize) + newline)

        #3
        connection_header = headers_list[3]
        headers += (connection_header + headers_default[3] + newline)
        #DONE



    elif code=="301":
        #need all headers

        #2
        loc_header = headers_list[2]
        headers += (loc_header + ext + newline)

        #0
        cont_type_header = headers_list[0]
        file_type = "text/html" #tell the user whats up with our own html
        headers += (cont_type_header + file_type + newline)

        #1
        cont_size_header = headers_list[1]
        content_bytesize = os.path.getsize(web_root+ext)
        headers += (cont_size_header + str(content_bytesize) + newline)
        
        #3
        connection_header = headers_list[3]
        headers += (connection_header + headers_default[3] + newline)


    elif code=="404" or code=="405":
        #0
        cont_type_header = headers_list[0]
        file_type = "text/html" #tell the user whats up with our own html
        headers += (cont_type_header + file_type + newline)

        #1
        cont_size_header = headers_list[1]
        content_bytesize = os.path.getsize(ext) #PROBLEMS FOR 405 LINE
        headers += (cont_size_header + str(content_bytesize) + newline)
        
        #3
        connection_header = headers_list[3]
        headers += (connection_header + headers_default[3] + newline)
        
    return headers


# the very first line of a response
def processFirstline(request_firstline):
    accepted_methods = {"GET"} #only need GET + assumes get req doesnt have a body
    firstline_parts = request_firstline.split()
    method = firstline_parts[0]
    url = firstline_parts[1]

    return method in accepted_methods, url

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8')) theirs

        

        #GOAL IS TO BUILD A RESPONSE
        response = ""  #Mmade of 4 things:1)first line(http type and status code), 2)headers 3)[A BLANK LINE] 4)a body

        resp_firstline = http #to start wil change
        resp_headers = ""
        resp_blankline = newline #always space between headers and response
        resp_body = ""

        #CHECK REQUEST FIRST LINE
        request = self.data.decode(encoding).split("\r\n")
        rq_firstline = request[0]

        method_accepted, url_requested = processFirstline(rq_firstline)
        #Handle Method 
        if not method_accepted:
            # print("NOT GETTING")
            status_code = "405"
            resp_firstline += status_codes[status_code]

            file_ext = "400html files/405.html" # to show them why
            resp_headers = addHeaders(status_code,file_ext)
            resp_body = addBody(status_code,file_ext)
            
            
        else:
            #CHECK PATH EXISTS

            up_movement = len(url_requested)>1 and url_requested[1]=="." #the first char sould not be a dot
            path_exists = os.path.exists(web_root+url_requested)

            if not path_exists or up_movement:
                # print("PATH DOESNT EXIST")
                status_code = "404"
                resp_firstline += status_codes[status_code]

                file_ext = "400html files/404.html" #specially made for 404elif code=="405":

                #add headers content type, content length, connection
                resp_headers = addHeaders(status_code, file_ext)
                
                #add body
                resp_body = addBody(status_code, file_ext)

            else: #200, 301, 404
                # print("PATH EXUTS")
                
                test_path = web_root+url_requested
                path_is_dir = os.path.isdir(test_path)
                has_slash = url_requested[len(url_requested)-1]=="/"

                if path_is_dir:
                    if not has_slash: #301

                        #first redirect
                        status_code = "301"
                        url_requested = withSlash(url_requested) #simply adds a slash



                    else: #has slash just check if has index,hetml
                        has_html = os.path.exists(test_path+"index.html")
                        if has_html: #200
                            status_code = "200"
                            url_requested += "index.html"
                          
                        else: #404
                            status_code = "404"
                            url_requested = "400html files/404.html"

                else: #path exist and its a file, show it
                    status_code = "200"
                            
                #
                

                resp_firstline += status_codes[status_code]
                resp_headers += addHeaders(status_code, url_requested)
                resp_body = addBody(status_code, url_requested)


        # BUILD RESPONSE FROM PARTS
        response = resp_firstline + newline + resp_headers + resp_blankline + resp_body

        #finally
        send(self.request, response)



            



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
#https://www.cs.unb.ca/~bremner/teaching/cs2613/books/python3-doc/library/socketserver.html
#https://docs.python.org/3/library/socket.html#other-functions
