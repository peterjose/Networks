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
clientSocket = socket(AF_INET, SOCK_STREAM)
# 
# Connect the client to the specified server
#
clientSocket.connect((serverURL, serverPort))
print("Client connected to server: " + serverURL + ":" + str(serverPort))
#
# This client implements the following scenario:
# 1. LIST_FILES
# 2a. UPLOAD the specified file
# 2b. Check MD5
# 3. LIST_FILES
# 4a. DOWNLOAD the previously uploaded file
# 4b. Check MD5
#
#close TCP connection

# path for download folder
path = './DownloadedFiles/'
if not os.path.exists(path):
    os.mkdir(path)

# Show the available commands 
input_option = input("Following commands are available: \nLIST_FILES \nUPLOAD \nDOWNLOAD\nexit\n")
input_option = input_option.split(' ')

if input_option[0] == "LIST_FILES":
    print("Sending command to list files")
    # send the LIST_FILES command to server
    clientSocket.send("LIST_FILES".encode())
    list = clientSocket.recv(1024)
    print(list.decode())
    
elif input_option[0] == "UPLOAD":
    print("Sending command to upload files")
    # send the upload command
    clientSocket.send("UPLOAD".encode())
    print(clientSocket.recv(1024).decode())
    # get the file information from user
    file_name= input("\nEnter file name : ")
    # check if file exists
    if not os.path.exists(file_name):
        print("file not present")
    else :
        file_size = os.path.getsize(file_name)
        #print("File size : " + file_size)
        # send the file information to server
        clientSocket.send((file_name+";"+str(file_size)).encode())
        # wait for server ack
        print(clientSocket.recv(1024).decode())
        file_send = open(file_name, "rb")
        while True:
            # read 1024 bytes in each iteration that can be send
            data_read = file_send.read(1024)
            if data_read:
                # send the data through the socket
                clientSocket.send(data_read)
            else:
                print("file has been sent")
                break
        # close the file
        file_send.close()
        # get the md5 hash from server
        md5_hash_val_from_server = clientSocket.recv(1024).decode()
        file_data = pathlib.Path('./'+file_name).read_bytes()
        # md5 is generated using the file data
        md5_hash_val_send_file = generate_md5_hash(file_data)
        # cross check the md5 hash to verify
        if md5_hash_val_from_server == md5_hash_val_send_file:
            print ("Success")
        else:
            print ("Fail")
elif input_option[0] == "DOWNLOAD":
    print("Sending command to download files")
    # send download command
    clientSocket.send("DOWNLOAD".encode())
    print(clientSocket.recv(1024).decode())
    # get the file id
    file_id= input("\nEnter file id : ")
    clientSocket.send((file_id).encode())
    # get the file information
    file_name , file_size = clientSocket.recv(1024).decode().split(";")
    file_size = int(file_size)
    # create the file in the download location
    file_rvd = open(path+file_name, "wb")
    i = 0
    while True:
        data_rvd = clientSocket.recv(1024)
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
    file_rvd.close()
    # open the filedata to find the md5
    file_data = pathlib.Path(path+file_name).read_bytes()
    # md5 is generated using the file data
    md5_string = generate_md5_hash(file_data)
    # cross check the ids 
    if md5_string == file_id:
        print("Success")
    else:
        print("Fail")
        
elif input_option[0] == "exit":
    print("Exiting Client ...")
else:
    print("invalid option")

clientSocket.close()
