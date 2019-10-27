import json
import re
import sys

def value_to_tuple(value):
    operators = { ">": ["gt"], ">=": ["gte"], "<": ["lt"], "<=": ["lte"], "!=": ["dne"],
        "-": ["-"], "+": ["+"], "/": ["/"], "*": ["*", "."]}
    things = ["gt", "lt", "gte", "lte", "dne",
              "-", "+", "/", "*"]

    var = 10

    # for each token in things
    for i in range(len(things)):
        if value.find(things[i]) != -1:
            if i <= 1 and value.find(things[i+2]) != -1:
                var = i + 2
                break
            else:
                var = i
                break

    if var != 10:
        m = re.search(r"\d", value).start()
        deb = value.find(things[var])
        if things[var] == "gt":
            s = ">"
        elif things[var] == "lt":
            s = "<"
        elif things[var] == "gte":
            s = ">="
        elif things[var] == "lte":
            s = "<="
        elif things[var] == "dne":
            s = "!="
        else:
            s = value[deb]

        name = value[:deb]
        val = value[m:]
        returnArray = [name, val, s]
    else:
        m = re.search(r"\d", value).start()
        name = value[:m]
        val = value[m:]
        returnArray = [name, val, "null"]

    return returnArray

def parse_rectangle(value):
    components = value_to_tuple(value)
    if components[2] != "null":
        line = components[0] + " = " + components[0] + " " + components[2] + " " + components[1]
    else:
        line = components[0] + ' = ' + components[1]
    return line

def parse_triangle(value):
    components = value_to_tuple(value)
    if components[2] != "null":
        line = "if " + components[0] + " " + components[2] + " " + components[1] + ":"
    else:
        line = "if " + components[0] + " == " + components[1] + ":"
    return line

def parse_ellipse(value):
    line = "print(\"" + value + "\")"
    return line

def parse_pentagon(value):
    components = value_to_tuple(value)
    if components[2] != "null":
        line = "while " + components[0] + " " + components[2] + " " + components[1] + ":"
    else:
        line = "while " + components[0] + " == " + components[1] + ":"
    return line

# open the data file
if len(sys.argv) > 1:
    data_file = open(sys.argv[1], "r")
else:
    data_file = open("../exampleIntermediaryJSON.json", "r")

# convert file data into python list
data = json.load(data_file)["shapes"]

# open the new python file to be created
script_file = open("./script.py", "w")

indentations = 0
is_last_if = False

# do something for each element in the array
for element in data:
    element["value"] = element["value"].lower()

    # If the value is end, we should
    if element["value"] == "end":
        indentations -= 1
        continue

    is_if = False
    shape_type = element["shape"]
    if shape_type == "rectangle" or shape_type == "square" or shape_type == "parallelogram" or shape_type == "trapezoid" or shape_type == "diamond" or shape_type == "quadrilateral":
        line = parse_rectangle(element["value"])
    elif shape_type == "triangle" or shape_type == "equilateralTriangle" or shape_type == "rightTriangle" or shape_type == "isoscelesTriangle":
        if element == data[-1]:
            is_last_if = True
        line = parse_triangle(element["value"])
        is_if = True
    elif shape_type == "ellipse" or shape_type == "circle":
        line = parse_ellipse(element["value"])
    elif shape_type == "pentagon":
        line = parse_pentagon(element["value"])
        is_if = True

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
