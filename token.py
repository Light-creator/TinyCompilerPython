import enum

class TokenType(enum.Enum):
    EOF = 0
    IDENT = 1
    UNDEFINED = 2
    STRING = 3
    NUMBER = 4
    NEWLINE = 5
    BRANCH = 6

    MINUS = 10
    PLUS = 11
    ASTERISK = 12
    SLASH = 13

    EQ = 20
    LT = 21
    GT = 22
    EQEQ = 23
    NOTEQ = 24
    LEQT = 25
    GEQT = 26
    BANG = 27
    BRL = 28
    BRR = 29

    WHILE = 30
    REPEAT = 31
    COLON = 32
    IF = 33
    ELSE = 34
    ELIF = 35
    PRINT = 36
    INPUT = 37

    LCRL = 40
    RCRL = 41
    FUNC = 42
    COMMA = 43
    RET = 44
    FBRANCH = 45
    LST = 46
    COND_BRANCH = 47

    SQBRL = 50 # [
    SQBRR = 51 # ]
    ARR_BRANCH = 52
    QUOTE = 53 # '
    CHAR = 54
    INT = 55
    ARR = 56
    INDEX = 57
    PRINTC = 58


class Token:
    def __init__(self, token_type, token_value):
        self.token_type = token_type
        self.token_value = token_value