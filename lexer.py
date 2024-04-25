from token import Token, TokenType

class Lexer:
    def __init__(self, _input):
        self.input = _input
        self.curr_pos = 0
        self.curr_char = _input[self.curr_pos]

    def skip_whitespaces(self):
        while self.curr_char == ' '  or self.curr_char == '\t':
            self.next_char() 

    def in_alphabet_scope(self, c):
        return c.isalpha() or c == "_" or c == "'"

    def read_alpha(self):
        token_str = ""
        while self.curr_char != ' ' and self.curr_char != '\0' and self.curr_char != '(' and self.curr_char != ',':
            token_str += self.curr_char
            if self.peek_char() in ",)( ':[]":
                break
            self.next_char()

        if token_str[0] == "'" and token_str[-1] == "'":
            return Token(TokenType.STRING, token_str)

        if token_str == "while":
            return Token(TokenType.WHILE, "while")
        elif token_str == "if":
            return Token(TokenType.IF, "if")
        elif token_str == "else":
            return Token(TokenType.ELSE, "else")
        elif token_str == "elif":
            return Token(TokenType.ELIF, "elif")
        elif token_str == "print":
            return Token(TokenType.PRINT, "print")
        elif token_str == "printc":
            return Token(TokenType.PRINTC, "printc")
        elif token_str == "input":
            return Token(TokenType.INPUT, "input")
        elif token_str == "func":
            return Token(TokenType.FUNC, "func")
        elif token_str == "ret":
            return Token(TokenType.RET, "ret")
        elif token_str == "Arr":
            return Token(TokenType.ARR, "Arr")
        elif token_str == "Int":
            return Token(TokenType.INT, "Int")
        elif token_str == "Char":
            return Token(TokenType.CHAR, "Char")
        else:
            return Token(TokenType.IDENT, token_str)

    def read_numeric(self):
        token_str = ""
        while self.curr_char not in ' \0),':
            if not self.curr_char.isdigit():
                print("Lexer Error: Wrong digit")
                return Token(TokenType.UNDEFINED, "UNDEFINED")
            token_str += self.curr_char

            if self.peek_char() in ':),]': break
            self.next_char()

        return Token(TokenType.NUMBER, token_str) 
            

    def next_char(self):
        self.curr_pos += 1
        if self.curr_pos >= len(self.input):
            self.curr_char = "\0"
        else:
            self.curr_char = self.input[self.curr_pos]

    def peek_char(self) -> str:
        if self.curr_pos+1 >= len(self.input):
            return "\0"
        else:
            return self.input[self.curr_pos+1]

    def get_token(self) -> Token:
        self.skip_whitespaces()
        # print(self.curr_char)

        token = Token(TokenType.UNDEFINED, "UNDEFINED")
        if self.curr_char == "+":
            token = Token(TokenType.PLUS, "+")
        elif self.curr_char == "-":
            token = Token(TokenType.MINUS, "-")
        elif self.curr_char == "*":
            token = Token(TokenType.ASTERISK, "*")
        elif self.curr_char == "/":
            token = Token(TokenType.SLASH, "/")
        elif self.curr_char == "[":
            token = Token(TokenType.SQBRL, "[")
        elif self.curr_char == "]":
            token = Token(TokenType.SQBRR, "]")
        elif self.curr_char == "\n":
            token = Token(TokenType.NEWLINE, "\n")
        elif self.curr_char == "\0":
            token = Token(TokenType.EOF, "\0")
        elif self.curr_char == ":":
            token = Token(TokenType.COLON, ":")
        elif self.curr_char == ",":
            token = Token(TokenType.COMMA, ",")
        elif self.curr_char == "'":
            token = Token(TokenType.QUOTE, "'")
        elif self.curr_char == "{":
            token = Token(TokenType.LCRL, "{")
        elif self.curr_char == "}":
            token = Token(TokenType.RCRL, "}")
        elif self.curr_char == "(":
            token = Token(TokenType.BRL, "(")
        elif self.curr_char == ")":
            token = Token(TokenType.BRR, ")")
        elif self.curr_char == "=":
            if self.peek_char() == "=":
                token = Token(TokenType.EQEQ, "==")
                self.next_char()
            else:
                token = Token(TokenType.EQ, "=")
        elif self.curr_char == "!":
            if self.peek_char() == "=":
                token = Token(TokenType.NOTEQ, "!=")
                self.next_char()
            else:
                token = Token(TokenType.BANG, "!")
        elif self.curr_char == ">":
            if self.peek_char() == "=":
                token = Token(TokenType.GEQT, ">=")
                self.next_char()
            else:
                token = Token(TokenType.GT, ">")
        elif self.curr_char == "<":
            if self.peek_char() == "=":
                token = Token(TokenType.LEQT, "<=")
                self.next_char()
            else:
                token = Token(TokenType.LT, "<")
        else:
            if self.in_alphabet_scope(self.curr_char):
                token = self.read_alpha()
            elif self.curr_char.isdigit():
                token = self.read_numeric()
            else:
                print("Lexer Error: Undefined Token")
                return token
        
        self.next_char()
        return token