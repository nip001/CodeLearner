from TokenType import *
import sys

class Lexer:
    def __init__(self,input):
        self.source = input + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''   # Current character in the string.
        self.curPos = -1    # Current position in the string.
        self.nextChar()

    #Prosses the next character
    def nextChar(self):
        self.curPos +=1
        if self.curPos >= len(self.source):
            self.curChar = '\0'#EOF
        else:
            self.curChar = self.source[self.curPos]

    #Returns the lookahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]

    #Invalid token found, print error message and exit
    def abort(self,message):
        sys.exit("Lexing error. "+message)

    #Skip whitespace except newLines, which  we will  use to indicate the end of a statement
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()

    #Skip comments int the code
    def skipComment(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()

    #Return next token
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-': 
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)
        elif self.curChar == '=':
            #check whether this token is = or == 
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == '<':
            #Check whether this token is < or <=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '>':
            #Check whether this token is > or >=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == '!':
            #Check whether this token is ! or != 
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar+self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !"+self.peek())
        elif self.curChar == '\"':
            #Get character between quotations
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\"':
                # Dont allow  special character in the string. No escape characters ,new lines, tabs, or %.
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string")
                self.nextChar()
            tokText = self.source[startPos : self.curPos] # get substring 
            token = Token(tokText,TokenType.STRING) 
        elif self.curChar.isdigit():
            #Leading character is a digit , so this  must be a number.
            #Get all consecutive digits and decimal if there is  one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': #Decimal
                self.nextChar()
                #Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    #Error!
                    self.abort("Illegal character in number")
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos+1] # get substring 
            token = Token(tokText,TokenType.NUMBER)
        elif self.curChar.isalpha(): 
            #Leading character is a letter , so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters 
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            #Check if  the  token is in the  list of keyword
            tokText = self.source[startPos : self.curPos+1] #Get  substring
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None : #Identifier
                token = Token(tokText,TokenType.IDENT)
            else: #Keyword
                token = Token(tokText,keyword)
        else:
            #Unknown Token
            self.abort("Unknown token: " + self.curChar)
        
        self.nextChar()
        return token


# Token contains the original text and the type of token.
class Token:
    def __init__(self,tokenText,tokenKind):
        self.text = tokenText #The token actually a text . Used for identifier ,strings, and numbers
        self.kind = tokenKind #The token type that this token is classified as.
    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None
