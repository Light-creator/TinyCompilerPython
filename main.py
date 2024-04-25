from lexer import Lexer
from token import TokenType
from parser import Parser
from tree_traverser import TreeTraverser

import os

def lexer_loop(lexer):
    token = lexer.get_token()
    while token.token_type != TokenType.EOF:
        if(token.token_type == TokenType.NEWLINE):
            print("New Line")
        else:
            print(token.token_type, token.token_value)
        token = lexer.get_token()

def main():
    f = open("examples/main.tl", "r")
    input_str = f.read().replace("\n", " \n ")+" \n "
    lexer = Lexer(input_str)
    parser = Parser(lexer)

    # lexer_loop(lexer)
    parser.program()

    parser.tree.print()

    traverser = TreeTraverser(parser.tree, parser.vars, parser.funcs_info)
    traverser.start_traverse()

    f.close()

if __name__ == "__main__":
    main()
