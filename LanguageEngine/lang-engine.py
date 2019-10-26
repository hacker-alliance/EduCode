import json

# Open the data file
data_file = open("../exampleIntermediaryJSON.json", "r")

# Convert file data into python list
data = json.load(data_file)

# Open the new python file to be created
file = open("./script.py", "w")

# Do something for each element in the array
for element in data:
    # print(element["shape"])
    line = ""
    # determine what kind of shape it is
    if element["shape"] == "rectangle":
        print(element["value"])

print(data)
