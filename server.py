# SERVER.PY

import socket
import threading
import sqlite3
import time
import os
import file

write_lock = threading.Lock()

class ServerSocket:
    DELIMITER = "||DELIMITER||"

    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.sock = None

    def bindSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.HOST, self.PORT))

    def listen(self):
        self.sock.listen()

    def acceptClient(self):
        self.c_sock, addr = self.sock.accept()
        print(f"accepted client connection {addr[1]}")

    def send(self, message):
        self.c_sock.sendall(message.encode())

    def receive(self, buff_size=1024):
        return self.c_sock.recv(buff_size).decode()

    def createNewImage(self):
        PHOTO_DIR = "serverFiles/"

        # lock other threads from writing
        
        # open sql connection
        database = sqlite3.connect("photo_server.db")
        cursor = database.cursor()

        # create table for photos in db
        cursor.execute("""CREATE TABLE IF NOT EXISTS
            photo(file_name, file_dir, upload_date, tags)""")

        # receive first packet
        received_packet = self.receive()
        name, size, date, tags = received_packet.split(self.DELIMITER)
        dir = PHOTO_DIR + name
        size = int(size)
        print(name, size, date, tags)

        # create new entry to database NEEDS WRITE LOCK
        with write_lock:
            cursor.execute("INSERT INTO photo values(?,?,?,?)",
                            (name, dir, date, tags))
            database.commit()

        # wait to recieve the data
        data = self.c_sock.recv(size)
        if not data:
            print("Data was not recieved")
            return

        photo_path = PHOTO_DIR + name
        file.writeBinaryToFile(photo_path, data)

        # send confirmation message and close database
        self.send("message received!")
        database.close()

    def sendImage(self, file_dir):
        binary_data = file.readFileBinary(file_dir)
        data_size = str(len(binary_data))
        _, file_name = file_dir.split('/')
        print(file_name)
        
        self.send(data_size)
        time.sleep(.01)
        self.c_sock.sendall(binary_data)

    # loops sendImage for all dirs in matching_files, sends "None" to signify end
    def sendImages(self, matching_files):
        print(matching_files)
        for file_dir in matching_files:
            print(file_dir)
            self.sendImage(file_dir)
        self.send("None")

    # all search functions return a list of strings containing file_dirs
    def searchByName(self, name):
        with sqlite3.connect("photo_server.db") as db:
            cur = db.cursor()
            rows = cur.execute("SELECT file_dir FROM photo WHERE file_name=?", (name,))
        
        rows = rows.fetchall()
        matching_files = self.listMatchingFilesFrom(rows)
        return matching_files
        
    def searchByDate(self, date):
        matching_files = []
        with sqlite3.connect("photo_server.db") as db:
            cur = db.cursor()
            cur_result = cur.execute("SELECT file_dir FROM photo WHERE upload_date=?", (date,))

        rows = cur_result.fetchall()
        matching_files = self.listMatchingFilesFrom(rows)
        return matching_files

    def searchByTags(self, tag_arg):
        DELIM = " "
        matching_files = []
        # fetch tags from db
        with sqlite3.connect("photo_server.db") as db:
            cur = db.cursor()
            tag_rows = cur.execute("SELECT file_dir, tags FROM photo")

        # loop through each entry that has tags
        while True:
            tag_row = tag_rows.fetchone()
            if tag_row == None: # if at end of rows
                break

            tag_list = tag_row[1] # get the string of tags
            tag_list = tag_list.split(DELIM)
            
            for tag in tag_list:
                if tag == tag_arg: # if match, add file_dir to list
                    matching_files.append(tag_row[0])

        if not matching_files:
            return None
        print(matching_files)
        return matching_files

    # NEEDS TO BE LOCKED
    def removeImage(self, file_dir):
        with write_lock:
            with sqlite3.connect("photo_server.db") as db:
                cur = db.cursor()
                cur.execute("DELETE FROM photo WHERE file_dir=?", (file_dir,))
                db.commit()
            try:
                os.remove(file_dir)
                self.send("File successfully deleted")
            except FileNotFoundError:
                self.send("File does not exist, or was already deleted")

    def listMatchingFilesFrom(self, rows):
        matching_files = []
        for row in rows:
            matching_files.append(row[0])
        return matching_files

    def clientHandler(self):
        DIR = "serverFiles/"
        # execute client requests
        option = self.receive()
        print(option)
        match option: # OPTION CHOICE 1
            case '1':
                self.createNewImage()
            case '2':
                option = self.receive()
                print(option)
                matching_files = []
                match option: # OPTION CHOICE 2
                    case "1":
                        name = self.receive()
                        matching_files = self.searchByName(name)
                    case "2":
                        date = self.receive()
                        matching_files = self.searchByDate(date)
                    case "3":
                        tag = self.receive()
                        matching_files = self.searchByTags(tag)
                    case "4":
                        pass
                    case _:
                        print("Invalid choice received :(")
                if option != "4":
                    self.sendImages(matching_files)
            case '3':
                file_name = self.receive()
                self.removeImage(DIR + file_name)

def startServer(HOST, PORT):
    s_sock = ServerSocket(HOST, PORT)
    s_sock.bindSocket()
    s_sock.listen()

    while True:
        s_sock.acceptClient()
        thread = threading.Thread(target=s_sock.clientHandler)
        thread.start()

def main():
    startServer("127.0.0.1", 12345)

if __name__ == "__main__":
    main()