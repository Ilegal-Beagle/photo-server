# Final Project Instructions
This should run perfectly fine on JuperLab, but just in case, you will need Python3

1. See if Python is installed
    * run `python3 --version`
    * if not, run `sudo apt install python3`

2. Run the server `python3 server.py`
3. Run a client `python3 client.py`

**Note:** I have attached a SQLite database for testing the functions of the server.
But you can leave it out and it'll make a new database.

# Challenges
* Trying to use Lua at fist
    * had to switch to python due to limitations of language
        * Could not make the server multithreaded
        * threads could not take in client object
* Undestanding how to send images over a TCP connection
* Learning to SQLite to keep track of the files in server
* Debugging

# Features
* Client can send photos to server
* Client can request photos by different means
    * ask for specific photo by name
    * ask for all photos by date
    * ask for all photos that have a tag attached to them
* Client can also delete a photo from the server by entering the name of the file