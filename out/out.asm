section    .text                
           global     _start    
_start:                         
           call       main_func 
           jmp        exit      
print_char_func:                      
           push       rbp       
           mov        rbp, rsp  
           mov        rax, [rbp + 16]
           push       rax       
           mov        rax, qword [rbp - 8]
           push       rax       
           mov        rax, 1    
           mov        rdi, 1    
           lea        rsi, qword [rsp]
           mov        rdx, 1    
           syscall              
           mov        rsp, rbp  
           pop        rbp       
           ret                  
main_func:                      
           push       rbp       
           mov        rbp, rsp  
           push       'a'       
           push       'b'       
           push       'c'       
           push       0         
           pop        rax       
           push       rax       
           jmp        loop_0    
loop_0:                         
           mov        rax, qword [rbp - 32]
           push       rax       
           push       3         
           pop        rax       
           pop        rbx       
           cmp        rbx, rax  
           jge        exit_loop_0
           mov        rax, qword [rbp - 32]
           push       rax       
           pop        rax       
           imul       rax, 8    
           add        rax, 8    
           mov        r10, rbp  
           sub        r10, rax  
           mov        rbx, qword [r10]
           push       rbx       
           call       print_char_func
           mov        rax, qword [rbp - 32]
           push       rax       
           push       1         
           pop        rax       
           pop        rbx       
           add        rbx, rax  
           push       rbx       
           pop        rax       
           mov        qword [rbp - 32], rax
           jmp        loop_0    
exit_loop_0:                      
           mov        rsp, rbp  
           pop        rbp       
           ret                  
                                
exit:                           
           mov        rax, 60   
           mov        rdi, 0    
           syscall              
