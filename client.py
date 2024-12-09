# CLIENT.PY

import socket
import time
import datetime
import file
from os import path
import re

# gets the date from the computer YYYY-MM-DD
#returns it as a STRING
def getDate():
        upload_date = datetime.datetime.now()
        upload_date = str(upload_date)[:10]
        return upload_date


class TCP:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port

    def createSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.HOST, self.PORT))

    def close(self):
        self.sock.close()

    def send(self, message):
        self.sock.sendall(message.encode())

    def receive(self, bytes=1024):
        try:
            return self.sock.recv(bytes).decode()
        except UnicodeDecodeError:
            print("Couldnt decode message recved.")

    def receiveImage(self, image_size):
        data = b''
        data += self.sock.recv(image_size)
        # subtract bytes recved from total image size
        # and request that many bytes till result equals 0
        while True:
            recv = image_size - len(data)
            if recv != 0:
                data += self.sock.recv(recv)
            else:
                return data

    def saveImageAs(self, data_size, file_name="serverImage.JPG"):
        data = self.receiveImage(data_size)
        file.writeBinaryToFile("SERVER"+file_name, data)

    # Loops receiveImage until there are no more files recved
    def receiveImages(self):
        count = 0
        while True:
            try:
                data_size = int(self.receive())
            except ValueError:
                break
            
            name = str(count) + ".JPG"
            self.saveImageAs(data_size, name)
            print("made file")
            count = count + 1

        print("\x1b[1m\nReceived all images!\x1b[22m\n")

    def sendImage(self, file_name, tags):
        DELIM = "||DELIMITER||"

        # create metadata
        binary_data = file.readFileBinary(file_name)
        data_size = str(len(binary_data))
        upload_date = getDate()
        
        # send metadata
        packet = (file_name + DELIM + data_size + DELIM + upload_date + DELIM + tags)
        self.send(packet)

        time.sleep(0.1)

        confirmation = self.receive()
        print(confirmation)
        if confirmation == "send data":
            time.sleep(.01)
            self.sock.sendall(binary_data)

        print(self.receive()) # confirmation message

    def getSearchParameters(self, option):
        match option: # OPTION CHOICE 2
            case "1":
                file_name = input("Enter file name: ")
                self.send(file_name)
            case "2":
                while True:
                    date = input("Enter date (YYYY-MM-DD): ")
                    pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'
                    match = re.findall(pattern, date)
                    if match:
                        print("BREAIK")
                        break
                    else:
                        print("please enter a valid data")
                    self.send(date)
            case "3":
                tag = input("Enter tag: ")
                self.send(tag)

def printTitle():
    ESC = "\x1b"
    BOLD = ESC + "[1m"
    RESET_BOLD = ESC + "[22m"
    print(BOLD + "************************************\n" +
                 "**                                **\n" +
                 "**  Welcome to the photo server!  **\n" +
                 "**                                **\n" + 
                 "************************************" + RESET_BOLD)

def printMenu():
    print("Select an option\n" +
             "\t1. Add photo\n" +
             "\t2. Request photo\n" +
             "\t3. Remove photo\n" +
             "\t4. Exit\n")

def printSearchMenu():
    print("Choose way to search\n" +
                    "\t1. file name\n" +
                    "\t2. date added\n" +
                    "\t3. by tag\n")

def getUserOption(min_value, max_value):
    while True:
        option = input("Enter a number: ")
        try:
            if min_value > int(option) > max_value:
                print("Please enter a valid integer.")
            else:
                break
        except ValueError:
            print("Please Enter a valid integer")
    return option

def main():
    HOST = "127.0.0.1"
    PORT = 12345

    # set up socket
    tcp = TCP(HOST, PORT)
    tcp.createSocket()
    tcp.connect()

    printTitle()
    tcp.sock.settimeout(2)

    while True:
        printMenu()
        option = getUserOption(1, 4)
        tcp.send(option)

        match option: # OPTION CHOICE 1
            case '1':
                while True:
                    file_name = input("Enter file name: ")
                    if (path.exists(file_name) and
                        file_name.endswith((".png", ".jpg", ".jpeg", ".JPG"))):
                        tags = input("Enter tags to attach to photo (hit enter if none): ")
                        tcp.sendImage(file_name, tags)
                        break
                    else:
                        print("File not found, or file type isnt supported.\n"+
                              "please enter a file in this directory")
            case '2':
                printSearchMenu()
                option = getUserOption(1, 3)
                tcp.send(option)
                tcp.getSearchParameters(option)
                tcp.receiveImages()
            case '3':
                file_name = input("Enter file name: ")
                tcp.send(file_name)
                print(tcp.receive())
            case '4':
                print("Closing connection to server")
                break
    tcp.close()

if __name__ == "__main__":
    main()