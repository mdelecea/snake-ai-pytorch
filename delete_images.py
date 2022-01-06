import os
files_in_directory = os.listdir("./")
for file in files_in_directory:
    if file.endswith(".jpeg"):
        os.remove(file)