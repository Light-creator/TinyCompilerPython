import sys

from lexer import Lexer
from tree import Tree, Node
from token import TokenType, Token

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.curr_token = None
        self.peek_token = None

        self.tree = Tree()

        self.next_token()
        self.next_token()

        # HashMap (name => offset)
        self.vars = {}
        self.funcs_info = {}
        self.curr_func = ""

    def next_token(self):
        self.curr_token = self.peek_token
        if self.peek_token != TokenType.EOF:
            self.peek_token = self.lexer.get_token()

    def program(self):
        while self.curr_token.token_type == TokenType.NEWLINE:
            self.next_token()
        
        while self.curr_token.token_type != TokenType.EOF:
            self.statement()

    def statement(self):
        tk_type = self.curr_token.token_type

        if tk_type == TokenType.RCRL:
            return None

        if tk_type == TokenType.PRINTC:
            self.tree.insert(self.curr_token)
            self.next_token()

            self.tree.curr_ptr.right = self.parse_expression()
            
            while self.curr_token.token_type != TokenType.NEWLINE:
                self.next_token()
    
        elif tk_type == TokenType.IDENT:
            if self.peek_token.token_type != TokenType.BRL:
                self.tree.insert(self.curr_token)

            if self.peek_token.token_type == TokenType.EQ:
                self.next_token()
                self.next_token()
                if self.curr_token.token_type == TokenType.STRING:
                    self.tree.curr_ptr.right = Node(self.curr_token)
                else:
                    self.tree.curr_ptr.right = self.parse_expression()
            elif self.peek_token.token_type == TokenType.BRL:
                self.tree.curr_ptr.left = self.parse_expression()
                self.tree.curr_ptr = self.tree.curr_ptr.left 

        elif tk_type == TokenType.IF or tk_type == TokenType.ELIF or tk_type == TokenType.ELSE:
            save_node_if = None
            if tk_type == TokenType.IF:
                self.tree.insert(Token(TokenType.COND_BRANCH, "cond_branch"))
                save_node_if = self.tree.curr_ptr
                self.tree.curr_ptr.right = Node(self.curr_token)
                self.tree.curr_ptr = self.tree.curr_ptr.right
            else:
                self.tree.insert(self.curr_token)
            self.next_token()
            
            self.tree.curr_ptr.right = Node(Token(TokenType.BRANCH, "branch"))
            
            if tk_type != TokenType.ELSE:
                self.tree.curr_ptr.right.right = self.parse_condition()

            self.match(TokenType.LCRL)
            self.match(TokenType.NEWLINE)
            
            save_node = self.tree.curr_ptr
            self.tree.curr_ptr = self.tree.curr_ptr.right

            while self.curr_token.token_type != TokenType.RCRL:
                self.statement()

            self.tree.curr_ptr.left = Node(Token(TokenType.RCRL, "RCRL"))
            self.tree.curr_ptr = save_node
            print(tk_type)
            self.match(TokenType.RCRL)

            while self.curr_token.token_type in [TokenType.ELIF,TokenType.ELSE] or self.peek_token.token_type in [TokenType.ELIF,TokenType.ELSE]:
                if self.curr_token.token_type == TokenType.NEWLINE:
                    self.next_token()
                self.statement()

            self.tree.curr_ptr = save_node_if

        elif tk_type == TokenType.WHILE:
            self.tree.insert(self.curr_token)
            self.next_token()

            self.tree.curr_ptr.right = Node(Token(TokenType.BRANCH, "branch"))
            self.tree.curr_ptr.right.right = self.parse_condition()

            self.match(TokenType.LCRL)
            self.match(TokenType.NEWLINE)

            save_node = self.tree.curr_ptr
            self.tree.curr_ptr = self.tree.curr_ptr.right

            while self.curr_token.token_type != TokenType.RCRL:
                self.statement()

            self.tree.curr_ptr.left = Node(Token(TokenType.RCRL, "RCRL"))

            self.tree.curr_ptr = save_node

            self.match(TokenType.RCRL)

        elif tk_type == TokenType.FUNC:
            self.tree.insert(self.curr_token)
            self.next_token()

            self.tree.curr_ptr.right = Node(Token(TokenType.BRANCH, "branch"))
            self.tree.curr_ptr.right.right = Node(self.curr_token)

            self.curr_func = self.curr_token.token_value
            self.funcs_info[self.curr_func] = "NO_RET"
            
            self.match(TokenType.IDENT)
            self.match(TokenType.BRL)

            curr_node = self.tree.curr_ptr.right.right
            while self.curr_token.token_type != TokenType.BRR and self.curr_token.token_type != TokenType.NEWLINE:
                if self.curr_token.token_type == TokenType.COMMA:
                    self.next_token()
                    continue
                # var: type
                curr_node.left = Node(self.curr_token) # var
                self.next_token()
                self.match(TokenType.COLON)
                curr_node = curr_node.left

                curr_node.right = Node(self.curr_token) # type
                if self.curr_token.token_type == TokenType.ARR:
                    token_buf = []
                    self.next_token()
                    self.next_token()
                    while self.curr_token.token_type != TokenType.SQBRR:
                        token_buf += [self.curr_token]
                        self.next_token()
                    self.next_token()
                    curr_node.right.left = self.parse_part_expression(token_buf, 0, len(token_buf))
                self.next_token()

            self.match(TokenType.BRR)
            self.match(TokenType.LCRL)
            self.match(TokenType.NEWLINE)

            save_node = self.tree.curr_ptr
            self.tree.curr_ptr = self.tree.curr_ptr.right

            while self.curr_token.token_type != TokenType.RCRL:
                self.statement()

            self.tree.curr_ptr.left = Node(Token(TokenType.RCRL, "RCRL"))

            self.tree.curr_ptr = save_node

            self.match(TokenType.RCRL)

        elif tk_type == TokenType.RET:
            self.tree.insert(self.curr_token)
            self.next_token()
            self.tree.curr_ptr.right = self.parse_expression()

            self.funcs_info[self.curr_func] = "RET"

        self.match(TokenType.NEWLINE)

    def parse_func(self, node):
        node.right = Node(Token(TokenType.FBRANCH, "func_branch"))
        node.right.right = Node(self.curr_token)
        self.next_token()

        self.match(TokenType.BRL)
        
        node_ptr = node.right
        while self.curr_token.token_type != TokenType.BRR:
            if self.curr_token.token_type == TokenType.COMMA:
                self.next_token()
                continue
            node_ptr.left =  Node(self.curr_token)
            node_ptr = node_ptr.left
            self.next_token()

        self.match(TokenType.BRR)


    def match(self, token_type) -> bool:
        if self.curr_token.token_type != token_type:
            sys.exit(f"Parsing Error: Types do not match (Actual: {self.curr_token.token_type} but expects {token_type})")
        self.next_token()

    def parse_condition(self) -> Node:
        token_buf = []
        compare_elements = [TokenType.GEQT, TokenType.LEQT, TokenType.NOTEQ, TokenType.EQEQ, TokenType.GT, TokenType.LT]
        cmp_idx = -1

        i = 0
        while self.curr_token.token_type != TokenType.NEWLINE and self.curr_token.token_type != TokenType.LCRL:
            token_buf += [self.curr_token]
            if self.curr_token.token_type in compare_elements:
                cmp_idx = i
            self.next_token()
            i += 1

        if cmp_idx == -1:
            sys.exit(f"Parsing Error: CMP element does not be found")

        node = Node(token_buf[cmp_idx])
        node.right = self.parse_part_expression(token_buf, cmp_idx+1, len(token_buf))
        node.left = self.parse_part_expression(token_buf, 0, cmp_idx)

        return node

    def parse_expression(self) -> Node:
        token_buf = []
        while self.curr_token.token_type != TokenType.NEWLINE:
            token_buf += [self.curr_token]
            self.next_token()
        
        return self.parse_part_expression(token_buf, 0, len(token_buf))


    def parse_func_expression(self, token_buf, start, end) -> Node:
        node = Node(Token(TokenType.FBRANCH, "func_branch"))
        node.right = Node(token_buf[start])
        node.right.left = Node(Token(TokenType.LST, "lst"))

        start += 2
        end_ptr = start
        while end_ptr < end and token_buf[end_ptr].token_type != TokenType.BRR:
            while token_buf[end_ptr].token_type != TokenType.BRR and token_buf[end_ptr].token_type != TokenType.COMMA:
                end_ptr += 1
            
            if end_ptr - start > 0:
                node_arg = self.parse_part_expression(token_buf, start, end_ptr)
                node.right.left.lst += [node_arg]
            
            end_ptr += 1
            start = end_ptr   

        return node

    def parse_arr_expression(self, token_buf, start, end) -> Node:
        node = Node(Token(TokenType.ARR_BRANCH, "arr_branch"))

        # check array type (char, int)
        flag_type = TokenType.INT # int
        if token_buf[start+1].token_type == TokenType.QUOTE: 
            node.right = Node(Token(TokenType.CHAR, "char"))
            start += 2
            flag_type = TokenType.CHAR
        else:
            node.right = Node(Token(TokenType.INT, "int"))
            start += 1

        node.left = Node(Token(TokenType.LST, "lst"))
        end_ptr = start
        while end_ptr < end:
            if token_buf[end_ptr].token_type == TokenType.COMMA or token_buf[end_ptr].token_type == TokenType.QUOTE or token_buf[end_ptr].token_type == TokenType.SQBRR:
                end_ptr += 1
                continue
            
            node_arg = None
            if flag_type == TokenType.INT:
                node_arg = Node(Token(TokenType.INT, token_buf[end_ptr].token_value))
            else:
                node_arg = Node(Token(TokenType.CHAR, token_buf[end_ptr].token_value))
            
            if node_arg != None:
                node.left.lst += [node_arg]

            end_ptr += 1

        return node

    def parse_indexed_expression(self, token_buf, start, end) -> Node:
        node = Node(Token(TokenType.INDEX, "index"))

        node.right = Node(token_buf[start])
        node.left = self.parse_part_expression(token_buf, start+2, end-1)

        return node
        
    def parse_part_expression(self, token_buf, start, end) -> Node:
        if(end - start <= 1):
            return Node(token_buf[start])

        # Array -> [1, 2, 3]
        if token_buf[start].token_type == TokenType.SQBRL and token_buf[end-1].token_type == TokenType.SQBRR:
            return self.parse_arr_expression(token_buf, start, end)

        # Func call -> add(x, y) + 1 - 3
        if token_buf[start].token_type == TokenType.IDENT and token_buf[end-1].token_type == TokenType.BRR:
            return self.parse_func_expression(token_buf, start, end)

        # Idexed value -> arr[0]
        if token_buf[start].token_type == TokenType.IDENT and token_buf[end-1].token_type == TokenType.SQBRR:
            return self.parse_indexed_expression(token_buf, start, end)

        min_precedence = 3
        min_idx = -1
        count_brackets = 0
        flag_brackets = False

        for i in range(start, end):
            if token_buf[i].token_type == TokenType.BRL or token_buf[i].token_type == TokenType.SQBRL:
                flag_brackets = True
                count_brackets += 1
                continue
            elif token_buf[i].token_type == TokenType.BRL or token_buf[i].token_type == TokenType.SQBRR:
                count_brackets -= 1
                continue

            if i+1 < end and token_buf[i].token_type == TokenType.IDENT and token_buf[i+1].token_type == TokenType.BRL:
                while token_buf[i].token_type != TokenType.BRR:
                    i += 1
                i += 1 
                
                if i == end: break

            if count_brackets == 0:
                precedence = self.get_precedence(token_buf[i].token_type)
                if min_precedence >= precedence:
                    min_precedence = precedence
                    min_idx = i
        
        if min_idx == -1 and flag_brackets:
            return self.parse_part_expression(token_buf, start+1, end-1)

        node = Node(token_buf[min_idx])
        node.right = self.parse_part_expression(token_buf, min_idx+1, end)
        node.left = self.parse_part_expression(token_buf, start, min_idx)

        return node

    def get_precedence(self, token_type):
        if token_type == TokenType.NUMBER or token_type == TokenType.IDENT:
            return 2
        elif  token_type == TokenType.PLUS or token_type == TokenType.MINUS:
            return 0
        elif  token_type == TokenType.ASTERISK or token_type == TokenType.SLASH:
            return 1
        return -1
