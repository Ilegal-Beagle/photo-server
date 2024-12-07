# CLIENT.PY

import socket
import time
import datetime
import file

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

    def receive(self, bytes):
        return self.sock.recv(bytes).decode()

    def receiveImage(self, file_name="serverImage.JPG"):
        data_size = self.receive(1024)
        if data_size == "None": # bound check
            return False

        data_size = int(data_size)
        data = self.sock.recv(data_size)

        file.writeBinaryToFile("SERVER"+file_name, data)
        return True

    # Loops receiveImage until there are no more files recved
    def receiveImages(self):
        count = 0
        while True:
            name = str(count) + ".JPG"
            success = self.receiveImage(name)
            if not success:
                break
            count = count + 1
        print("Received all images!")

    def sendImage(self, file_name, tags):
        DELIM = "||DELIMITER||"

        # create metadata
        binary_data = file.readFileBinary(file_name)
        data_size = str(len(binary_data))
        upload_date = getDate()
        
        # send metadata
        packet = (file_name + DELIM +
                data_size + DELIM +
                upload_date + DELIM +
                tags)

        self.send(packet)

        time.sleep(.01)

        # send  data
        self.sock.sendall(binary_data)

    def getSearchParameters(self, option):
        match option: # OPTION CHOICE 2
            case "1":
                file_name = input("Enter file name: ")
                self.send(file_name)
            case "2":
                date = input("Enter date (YYYY-MM-DD): ")
                self.send(date)
            case "3":
                tag = input("Enter tag: ")
                self.send(tag)

    def removeImage(self):
        pass

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

def main():
    HOST = "127.0.0.1"
    PORT = 12345

    # set up socket
    tcp = TCP(HOST, PORT)
    tcp.createSocket()
    tcp.connect()

    printTitle()

    while True:
        printMenu()
        option = getUserOption(1, 4)
        tcp.send(option)

        match option: # OPTION CHOICE 1
            case '1':
                file_name = input("Enter file name: ")
                tags = input("Enter tags to attach to photo (hit enter if none): ")
                tcp.sendImage(file_name, tags)
            case '2':
                printSearchMenu()
                option = getUserOption(1, 3)
                tcp.send(option)
                tcp.getSearchParameters(option)
                tcp.receiveImages()
            case '3':
                file_name = input("Enter file name: ")
                tcp.send(file_name)
            case '4':
                print("Closing connection to server")
                break
    tcp.close()

if __name__ == "__main__":
    main()