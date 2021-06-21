## Tested with python 3.8

# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
import os
import pathlib
#
# Generate md5 hash function
#
def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)
# 
# Define Server URL and PORT
#
serverPort = 7700
serverURL = "localhost"
# 
# Create TCP socket for future connections
#
serverSocket = socket(AF_INET, SOCK_STREAM)
# 
# Bind URL and Port to the created socket
#
serverSocket.bind((serverURL, serverPort))
# 
# Start listening for incoming connection (1 client at a time)
#
serverSocket.listen(1)
print("Server is listening on port: " + str(serverPort))

# path for server database
path = './ServerFileSystem'
if not os.path.exists(path):
    os.mkdir(path)

while True:
    # 
    # Accept incoming client connection
    #
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))
    data_rvd = connectSocket.recv(1024).decode()
    #print(data_rvd)
    
    ## if command is list files
    if data_rvd == "LIST_FILES":
        print("server received list command")
        # get the files in the server location
        entries = os.listdir(path)
        string = ""
        # check if there are no files in the database
        if not entries:
            string = "No files available at the moment"
        else:
            for ent in entries:
                # file data is read
                file_data = pathlib.Path(path+'/'+ent).read_bytes()
                # md5 is generated using the file data
                string += generate_md5_hash(file_data)
                string += ";" + ent + ";"
                string += str(os.path.getsize(path+'/'+ent)) + "\n"
        # reply is send back to the client
        connectSocket.send(string.encode())
    
    elif data_rvd == "UPLOAD":
        print("server received upload command")
        connectSocket.send("Please send the file name and file size".encode())
        # get file information
        file_name , file_size = connectSocket.recv(1024).decode().split(";")
        print("Received file name " + file_name + " and size " + file_size)
        file_size = int(file_size)
        # ack the client that server is ready
        connectSocket.send("Server Ready to accept file".encode())
        file_rvd = open(path+'/'+file_name, "wb")
        i = 0
        while True:
            data_rvd = connectSocket.recv(1024)
            i += 1024 
            if data_rvd:    
                file_rvd.write(data_rvd)
            else :
                print("data received completely")
                break
            # check if the complete file has been received
            if i >= file_size:
                print("data received completely")
                break
        # close the file
        file_rvd.close()
        # open the filedata to find the md5
        file_data = pathlib.Path(path+'/'+file_name).read_bytes()
        # md5 is generated using the file data
        md5_string = generate_md5_hash(file_data)
        # send the md5 hash value to the client
        connectSocket.send(md5_string.encode())
        print("md5 send to client")
    
    elif data_rvd == "DOWNLOAD":
        print("Server received command for downloading")
        connectSocket.send("Please send a file ID".encode())
        file_id = connectSocket.recv(1024).decode()
        entries = os.listdir(path)
        flag = True
        # check if there are no files in the database
        if not entries:
            flag = False
        else:
            for ent in entries:
                # file data is read
                file_data = pathlib.Path(path+'/'+ent).read_bytes()
                # checking matching file id
                if file_id == generate_md5_hash(file_data):
                    flag = True
                    print("file found " + ent)
                    # send the file information
                    connectSocket.send((ent+";"+str(os.path.getsize(path+'/'+ent))).encode())
                    # open file to send
                    file_send = open(path +'/'+ent, "rb")
                    while True:
                        # read 1024 bytes in each iteration that can be send
                        data_read = file_send.read(1024)
                        if data_read:
                            # send the data through the socket
                            connectSocket.send(data_read)
                        else:
                            print("file has been sent to client")
                            break
                    file_send.close()
                    break
        # if the file is not present
        if flag == False:
            connectSocket.send("FileError;0".encode())
            
    #close TCP connection
    connectSocket.close()