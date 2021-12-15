from lex import *
from TokenType import *
from parse import *
from emit import *
from flask import Flask,jsonify,request,make_response


import subprocess

import subprocess
import sys


#Service Declared 
app = Flask(__name__)
app.config["DEBUG"] =True


def main():
    # print("CodeLearner Compiler")
    # if len(sys.argv) != 2:
    #     sys.exit("Error: Compiler need source file for an argument")
    # with open(sys.argv[1], 'r') as inputFile:
    #     input = inputFile.read()
        
    # input = "IF WHILE mantap +-123 foo*THEN/"
    # lexer = Lexer("\nLET nums = 5\nPRINT \"What is the Fibonacci of 5?\"\nLET a = 0\nLET b = 1\nWHILE nums > 1 REPEAT\n    LET c = a + b\n    LET a = b\n    LET b = c\n    LET nums = nums - 1\nENDWHILE\nPRINT c")
    
    
    @app.route('/',methods=['POST'])
    def serviceCompiler():

        lexer = Lexer(request.json['code'])
        emitter = Emitter("out.c")
        parser = Parser(lexer,emitter)
        parser.program() 
        if(parser.parseError):
            return  make_response(jsonify({'output':parser.parseErrorMessage}),200)
        else:
            emitter.writeFile() # Write the output to file.
            subprocess.call(["gcc","out.c"])
            data = subprocess.check_output("./a.exe",universal_newlines=True)
            return make_response(jsonify({'output':data}),200)
    # print("Parsing Complete")

    # token = lexer.getToken()
    # while token.kind != TokenType.EOF:
    #     print(token.kind)
    #     token = lexer.getToken()
    app.run()


main()
# data = subprocess.check_output("./a.exe",universal_newlines=True)
# print("data adalah "+ data)