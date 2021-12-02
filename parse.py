import sys
from lex import *

#Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self,lexer,emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.parseError = False
        self.parseErrorMessage = ""


        self.symbols = set() #variable declared so far
        self.labelsDeclared = set() #label declared so far
        self.labelsGotoed = set() #label goto'ed so far
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() #Call twice cause to initialize current and peek

    #Return true if the token matches.
    def checkToken(self,kind):
        return kind == self.curToken.kind

    #Return true if next token matches.
    def checkPeek(self,kind):
        return kind == self.peekToken.kind

    #Try to matches current token. if not, error. Advances the current token. 
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    #Advances the current token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self,message):
        self.parseError = True
        self.parseErrorMessage = "Error. " + message
        # sys.exit("Error. "+ message)

    #Production rules.
    #Program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        #sinces some new line are required in our grammar, need to skip excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        #parse all the statement in the program .
        while not self.checkToken(TokenType.EOF):
            self.statement()

        #Wrap the things up 
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)



    def statement(self):
        #Check the first token to see what kind of statement this is
        #"PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                #Simple String.
                self.emitter.emitLine("printf(\""+ self.curToken.text +"\\n\");")
                self.nextToken()

            else:
                #Expected expression
                self.emitter.emit("printf(\"%"+".2f\\n\",(float)(")
                self.expression()
                self.emitter.emitLine("));")


        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")
            
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        #Label ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()

            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text +":")
            self.match(TokenType.IDENT)

        #GOTO ident
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto "+self.curToken.text+";")
            self.match(TokenType.IDENT)

        #LET ident "=" Expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()

            #  Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float "+self.curToken.text +";")

            self.emitter.emit(self.curToken.text+" = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")

        #INPUT ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()
            
            #If variable doesn't already exist, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float "+self.curToken.text+";")
                
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\",&" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        else:
            self.abort("Invalid statement at "+self.curToken.text+" ( "+self.curToken.kind.name+" )")

        self.nl()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):

        self.expression()
        #Must be at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at : "+ self.curToken.text )

        #Can have 0 or more comparison operators and expression 
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) 

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()

        #Can we have 0 or more +/- and expression
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    def term(self):
        self.unary()
        #Can have 0 or more *// and expression
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        #Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            #error!
            self.abort("Unexpected token at "+ self.curToken.text)


    def nl(self):
        
        #Require at least one line
        self.match(TokenType.NEWLINE)

        #Allow extra line too
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()