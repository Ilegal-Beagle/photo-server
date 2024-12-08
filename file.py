# FUNCTIONS.PY

def writeBinaryToFile(photo_path, data):
    with open(photo_path, mode="wb") as out_file:
        out_file.write(data)

# gives the binary contents of file
# returns string of contents and string of size
def readFileBinary(file_name):
    try:
        file = open(file_name, mode='rb')
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        with open(file_name, mode='rb') as file:
            binary_data = file.read()
        return binary_data
