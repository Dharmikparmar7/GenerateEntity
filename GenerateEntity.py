import pyperclip as p

def convert(n):
    if n == "i":
        return str("SqlInt32")
    if n == "v":
        return str("SqlString")
    if n == "dt":
        return str("SqlDateTime")

code = ""

name = input("Enter Name of column => ")

while(not (name == "exit" or name == "0")):
    datatype = input("Enter datatype (i = int, v = string, dt = datetime) => ")
    
    code += "protected " + str(convert(datatype)) + " _" + name + ";\n\n"
    code += "public " + str(convert(datatype))  + " " + name + "\n" 
    code += "{\n"
    code += "\tget\n"
    code += "\t{\n"
    code += "\t\treturn _" + name + ";\n"
    code += "\t}\n"
    code += "\tset\n"
    code += "\t{\n"
    code += "\t\t_" + name + " = value;\n"
    code += "\t}\n"
    code += "}\n\n"

    name = input("Enter Name of column => ")

p.copy(code)
