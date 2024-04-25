from token import TokenType

class Node:
    def __init__(self, token):
        self.token = token
        self.left = None
        self.right = None
        self.lst = []

class Tree:
    def __init__(self):
        self.head = None
        self.curr_ptr = None

    def insert(self, token):
        node = Node(token)
        if self.head == None:
            self.head = node
            self.curr_ptr = node
        else:
            self.curr_ptr.left = node
            self.curr_ptr = self.curr_ptr.left

    def print_node(self, node, offset):
        if node != None:
            offset_str = "  " * offset
            print(f"{offset_str}{node.token.token_value} -> [")
            if node.token.token_type == TokenType.LST:
                print(node.token.token_type, node.token.token_value)
                for l in node.lst: 
                    self.print_node(l, offset+1)
                return None
            
            print(offset_str + "left:")
            self.print_node(node.left, offset+1)
            print(offset_str + "right:")
            self.print_node(node.right, offset+1)
            print(offset_str + "]")

    def print(self):
        self.print_node(self.head, 0)