import json
import re

def value_to_tuple(value):
    m = re.search(r"\d", value).start()
    name = value[:m]
    val = value[m:]
    return name, val

def parse_rectangle(value):
    components = value_to_tuple(value)
    line = components[0] + ' = ' + components[1]
    return line

def parse_triangle(value):
    if value == "end":
        return value
    components = value_to_tuple(value)
    line = "if " + components[0] + " == " + components[1] + ":"
    return line

def parse_ellipse(value):
    line = "print(\"" + value + "\")"
    return line

def parse_hexagon(value):
    line = "while " + value + ":"
    return line

# open the data file
data_file = open("../exampleIntermediaryJSON.json", "r")

# convert file data into python list
data = json.load(data_file)

# open the new python file to be created
script_file = open("./script.py", "w")

indentations = 0
is_last_if = False

# do something for each element in the array
for element in data:
    is_if = False
    shape_type = element["shape"]
    if shape_type == "rectangle":
        line = parse_rectangle(element["value"])
    elif shape_type == "triangle":
        if element == data[-1]:
            is_last_if = True
        line = parse_triangle(element["value"])
        is_if = True
    elif shape_type == "ellipse":
        line = parse_ellipse(element["value"])
    elif shape_type == "hexagon":
        line = parse_hexagon(element["value"])
        is_if = True

    if line == "end":
        indentations -= 1
        continue

    # prepend indentations
    for i in range(indentations):
        line = "    " + line

    script_file.write(line + "\n")

    if is_if:
        indentations += 1

    line = ""

    if is_last_if:
        for i in range(indentations):
            line = "    " + line
        script_file.write(line + "pass")

# close the files
data_file.close()
script_file.close()