from token import TokenType

class ScopeStack:
    def __init__(self):
        self.stack = []
        self.count_vars = 0
        self.var_offset = 8
    
    def find_var_by_name(self, name):
        for table in self.stack:
            if name in table:
                # return var_offset, var_size
                return table[name][0], table[name][1]

        return None, None

    def pop(self):
        self.count_vars -= len(self.stack[-1])
        
        _sum = 0
        for var in self.stack[-1]:
            _sum +=  self.stack[-1][var]
        self.var_offset -= _sum

        self.stack = self.stack[:-1]

    def push(self, table):
        # table = HashMap -> [var_name => [var_offset, var_size]]
        self.stack += [table]

    def insert_in_last_table(self, var_name, var_size):
        self.stack[-1][var_name] = [self.var_offset, var_size]
        self.var_offset += var_size
        self.count_vars += 1

class FuncEntity:
    def __init__(self, name):
        self.name = name
        self.rsp_offset = 0

        self.args = {}
        self.offset_lst = [0]
        self.scope_stack = ScopeStack()

class TreeTraverser:
    def __init__(self, tree, _vars, funcs_info):
        self.f_asm = open("out/out.asm", "w")
        self.tree = tree
        self.vars = _vars

        self.loop_count = 0
        self.if_count = 0

        self.func_stack = []
        self.funcs_info = funcs_info

    def start_traverse(self):
        self.output("section", ".text", "")
        self.output("", "global", "_start")
        self.output("_start:", "", "")
        self.output("", "call", "main_func")
        self.output("", "jmp", "exit")
        
        self.node_traverse(self.tree.head)

        # Exit program
        self.output("", "", "")
        self.output("exit:", "", "")
        self.output("", "mov", "rax, 60")
        self.output("", "mov", "rdi, 0")
        self.output("", "syscall", "")

    def node_traverse(self, node):
        if node == None:
            return None

        if node.token.token_type == TokenType.RCRL:
            return None 
        if node.token.token_type == TokenType.IDENT:
            self.ident_traverse(node)
        elif node.token.token_type == TokenType.WHILE:
            self.output("", "jmp", f"loop_{self.loop_count}")
            self.while_traverse(node)
        elif node.token.token_type == TokenType.COND_BRANCH:
            self.if_traverse(node.right)
        elif node.token.token_type == TokenType.FUNC:
            self.func_traverse(node)
        elif node.token.token_type == TokenType.RET:
            self.ret_traverse(node)
        elif node.token.token_type == TokenType.FBRANCH:
            self.func_branch_traverse(node)
        elif node.token.token_type == TokenType.PRINTC:
            self.printc_traverse(node)

        self.node_traverse(node.left)

    def printc_traverse(self, node):
        self.traverse_expression(node.right)

        self.output("", "mov", "rax, 1")
        self.output("", "mov", "rdi, 1")
        self.output("", "lea", "rsi, qword [rsp]")
        self.output("", "mov", "rdx, 1")
        self.output("", "syscall", "")

    def ret_traverse(self, node):
        self.traverse_expression(node.right)
        self.output("", "pop", "rax")

    def func_traverse(self, node):
        branch_node = node.right 
        func_name = branch_node.right.token.token_value

        func_obj = FuncEntity(func_name)

        # Store args in Dict to restore them on new stack frame
        node_ptr = node.right.right.left
        while node_ptr != None:
            var_size = 8
            if node_ptr.right.token.token_type == TokenType.ARR:
                var_size = int(node_ptr.right.left.token.token_value)*8

            func_obj.offset_lst += [func_obj.offset_lst[-1] + var_size]
            func_obj.args[node_ptr.token.token_value] = var_size

            node_ptr = node_ptr.left

        self.func_stack += [func_obj]

        # Function Header
        self.output(f"{func_name}_func:", "", "")            
        self.output("", "push", "rbp")            
        self.output("", "mov", "rbp, rsp")

        # New Stack frame scope
        local_table = {}
        self.func_stack[-1].scope_stack.push(local_table)

        # Store args to new stack frame (according to their sizes)
        idx = len(func_obj.offset_lst)-1

        last_scope_offset = func_obj.offset_lst[idx] + 8
        for k in func_obj.args:
            self.func_stack[-1].scope_stack.insert_in_last_table(k, 8)
            print(self.func_stack[-1].scope_stack.stack)
            var_size = func_obj.args[k]

            for tmp_offset in range(last_scope_offset, last_scope_offset-var_size, -8):
                self.output("", "mov", f"rax, [rbp + {tmp_offset}]")
                self.output("", "push", f"rax")

            last_scope_offset -= var_size

            idx -= 1

        # Function Body
        self.node_traverse(branch_node.left)

        self.func_stack = self.func_stack[:-1]

        # Function Footer
        self.output("", "mov", "rsp, rbp")
        self.output("", "pop", "rbp")
        self.output("", "ret", "")

    def ident_traverse(self, node):
        self.traverse_expression(node.right)
        self.var_traverse(node)

    def func_branch_traverse(self, node):
        self.traverse_expression(node)

    def var_traverse(self, node):
        tk = node.token
        
        variable_offset, variable_size = self.func_stack[-1].scope_stack.find_var_by_name(tk.token_value)
        if variable_offset != None:
            self.output("", "pop", f"rax")
            offset = variable_offset
            if node.right.token.token_type == TokenType.INDEX:
                offset = variable_offset + (int(node.right.left.token.token_value)-1)*8
            self.output("", "mov", f"qword [rbp - {offset}], rax")
        else:
            if node.right.token.token_type == TokenType.ARR_BRANCH:
                arr_size_bits = len(node.right.left.lst)*8
                self.func_stack[-1].scope_stack.insert_in_last_table(tk.token_value, arr_size_bits)
            else:
                self.output("", "pop", f"rax")
                self.func_stack[-1].scope_stack.insert_in_last_table(tk.token_value, 8)
                self.output("", "push", "rax")

    def recursion_if_traverse(self, node, exit_label):
        if node == None: return None

        local_table = {}
        self.func_stack[-1].scope_stack.push(local_table)

        success_label = f"success_if_{self.if_count}"
        print(node.token.token_type)
        if node.token.token_type != TokenType.ELSE:
            comparison_node = node.right.right
            self.traverse_expression(comparison_node.left)
            self.traverse_expression(comparison_node.right)
            
            self.traverse_comparison(comparison_node, None, success_label)
        else:
            self.output("", "jmp", success_label)

        self.if_count += 1
        self.recursion_if_traverse(node.left, exit_label)

        self.output(f"{success_label}:", "", "")
        self.node_traverse(node.right.left)
        self.output("", "jmp", exit_label)

    def if_traverse(self, node):
        exit_label = f"exit_if_{self.if_count}"

        self.recursion_if_traverse(node, exit_label)

        self.output(f"{exit_label}:", "", "")
            
    def while_traverse(self, node):
        self.output(f"loop_{self.loop_count}:", "", "")

        local_table = {}
        self.func_stack[-1].scope_stack.push(local_table)

        # Loop comparison 
        comparison_node = node.right.right

        self.traverse_expression(comparison_node.left)
        self.traverse_expression(comparison_node.right)

        exit_label = f"exit_loop_{self.loop_count}"
        self.traverse_comparison(comparison_node, exit_label)

        # Loop body
        self.node_traverse(node.right.left)
        self.output("", "jmp", f"loop_{self.loop_count}")

        self.pop_vars_from_local_scope()

        # Loop exit
        self.output(f"{exit_label}:", "", "")


        self.loop_count += 1

    def traverse_comparison(self, node, exit_label=None, success_label=None):
        tk = node.token

        self.output("", "pop", "rax")
        self.output("", "pop", "rbx")
        self.output("", "cmp", "rbx, rax")

        if exit_label != None:
            if tk.token_type == TokenType.LT:
                self.output("", "jge", exit_label)
            elif tk.token_type == TokenType.GT:
                self.output("", "jle", exit_label)
            elif tk.token_type == TokenType.LEQT:
                self.output("", "jg", exit_label)
            elif tk.token_type == TokenType.GEQT:
                self.output("", "jl", exit_label)
            elif tk.token_type == TokenType.EQEQ:
                self.output("", "jne", success_label)
            elif tk.token_type == TokenType.NOTEQ:
                self.output("", "je", success_label)
        elif success_label != None:
            if tk.token_type == TokenType.LT:
                self.output("", "jl", success_label)
            elif tk.token_type == TokenType.GT:
                self.output("", "jg", success_label)
            elif tk.token_type == TokenType.LEQT:
                self.output("", "jle", success_label)
            elif tk.token_type == TokenType.GEQT:
                self.output("", "jge", success_label)
            elif tk.token_type == TokenType.EQEQ:
                self.output("", "je", success_label)
            elif tk.token_type == TokenType.NOTEQ:
                self.output("", "jne", success_label)

    def traverse_expression(self, node):
        tk = node.token

        if tk.token_type == TokenType.IDENT:
            offset, var_size = self.func_stack[-1].scope_stack.find_var_by_name(tk.token_value)
            if var_size <= 8:
                self.output("", "mov", f"rax, qword [rbp - {offset}]")
                self.output("", "push", "rax")
        elif tk.token_type == TokenType.NUMBER:
            self.output("", "push", tk.token_value)
        elif tk.token_type == TokenType.INDEX:
            # parse idx 
            self.traverse_expression(node.left)
            var_name = node.right.token.token_value
            var_offset, var_size = self.func_stack[-1].scope_stack.find_var_by_name(var_name)
            self.output("", "pop", "rax")
            self.output("", "imul", "rax, 8")
            self.output("", "add", "rax, 8")
            self.output("", "mov", "r10, rbp")
            self.output("", "sub", "r10, rax")
            self.output("", "mov", f"rbx, qword [r10]")
            self.output("", "push", "rbx")
        elif tk.token_type == TokenType.FBRANCH:
            args = node.right.left.lst
            for arg in args:
                self.traverse_expression(arg)
            self.output("", "call", f"{node.right.token.token_value}_func")
            
            if self.funcs_info[node.right.token.token_value] == "RET":
                self.output("", "push", "rax")
        elif tk.token_type == TokenType.ARR_BRANCH:
            arr_type = node.right.token.token_type
            elements = node.left.lst
            for el in elements:
                if arr_type == TokenType.INT:
                    self.output("", "push", f"{el.token.token_value}")
                else:
                    self.output("", "push", f"'{el.token.token_value}'")
        else:
            self.traverse_expression(node.left)
            self.traverse_expression(node.right)

            self.traverse_arithmetic(node)

    def traverse_arithmetic(self, node):
        tk = node.token
        
        self.output("", "pop", "rax")
        self.output("", "pop", "rbx")
        
        if tk.token_type == TokenType.PLUS:
            self.output("", "add", "rbx, rax")
        elif tk.token_type == TokenType.MINUS:
            self.output("", "sub", "rbx, rax")
        elif tk.token_type == TokenType.ASTERISK:
            self.output("", "mul", "rbx, rax")
        elif tk.token_type == TokenType.SLASH:
            self.output("", "div", "rbx, rax")
        
        self.output("", "push", "rbx")


    def output(self, fst, scd, thd):
        self.f_asm.write(f"{fst:10} {scd:10} {thd:10}\n")

    def get_offset(self, var_offset):
        return  (var_offset+1)*8

    def pop_vars_from_local_scope(self):
        sz = 0
        table = self.func_stack[-1].scope_stack.stack[-1]
        for el in table:
            sz += table[el][1] / 8

        for _ in range(sz):
            self.output("", "pop", "rax")
        self.func_stack[-1].scope_stack.pop()
