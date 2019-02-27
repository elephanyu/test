- awk
    - 基础
        - 设置多个分隔符  
            ```shell
            # 分隔符匹配一个或多个制表符或空格符
            awk -F"[\t ]+" '{print "device: "$1"\tfstype: "$3}' /etc/fstab
            ```   
        - begin end代码块
            ```shell
                >>> cat search.awk
                BEGIN {
                    print "How many people with nologin?"
                }
                # adder没有初始化直接拿来使用
                # 没处理输入数据的一条记录的过程中，adder变量原有的记录并没有被查出
                /nologin/ {++adder}
                END {
                    print "'nologin' appears "adder" times."
                }
                >>> awk -f search.awk /etc/passwd
            ```
        - 模式匹配
            ```shell
                >>> cat shell_record.awk
                BEGIN {
                    print "shell usage:"
                }
                /bash/ {++bash}
                /nologin/ {++nologin}
                END {
                    print "we have "bash" bash users."
                    print "we have "nologin" nologin users."
                }
                >>> awk -f shell_record.awk /etc/passwd
            ```
    - 变量与数组
        - 变量
            - 自定义变量 如adder、bash、nologin
            - 内建变量
                - FILENAME 当前输入文件的名称
                - FNR 当前输入文件的记录数
                - FS 字段分隔符（支持正则），默认为空格
                - NF 当前记录的字段数
                - NR 在工作中的记录数
                - OFS 输出字段分隔字符
                - ORS 处处记录分割字符（默认为"\n"）
                - RS 输入记录分割字符
            - 数组
                ```awk
                site["xx"]="xx"
                site["yy"]="yy"
                ```
            - 环境变量
                ```shell
                >>> awk 'BEGIN{print ENVIRON["HOME"]};print ENVIRON["PATH"]}'
                ```
    - 运算符
        - = += -= *= /= %= ^= **= 赋值
        - || && 逻辑或 逻辑与
        - ~ ~! 匹配正则表达式 不匹配正则表达式
        - < <= == > >= 关系运算符
        - 空格 连接
        - + - * / % 加 减 乘 除 求余
        - ^ *** 求幂
        - ++ -- 自加 自减
        - $ 字段引用
        - in 数组成员
    - 控制结构
        ```awk
        # if条件
        if (exp1) {
            statement1;
        } else if (exp2) {
            statement2;
        } else {
            statement3;
            statement4;
        }
        
        # while循环
        i = 4
        while ( i>=1 ) {
            print $i
            i--
        }
        
        # do while循环
        i = 4
        do {
            print $i
            i--
        } while ( i>=1 )
        
        # for循环
        for (x = 1; x <= 4; x++) {
            print x
        }
        
        # continue break
        x = 1
        while (1) {
            if (x==4) {
                x++
                continue
            }
            print "iteration", x
            if (x>20) {
                break
            }
            x++
        }
        ```
    - 自定义函数格式
        ```awk
        # 定义
        function funcname(arg1, arg2, ..., argn) {
            statement(s)
            return ret
        }
        # 调用
        funcname(expr1, expr2, ..., exprn)
        result = funcname(expr1, expr2, ..., exprn)
        ```
    - 引用传递(地址传递)和值传递
    - 递归调用
        ```shell
        >>> cat fib.awk
        function fib(nth)
        {
            if (nth == 1 || nth == 2)
                return 1
            } else {
                return fib(nth-1)+fib(nth-2)
            }
        }
        {
            n = $1
            printf("%dth of fib sequence is: %d\n", n, fib(n))
        }
        >>> echo "1\n2\n3\n10\n25\n50" | awk -f fib.awk 
        ```
    - 格式化输出
        - printf和sprintf一样，sprintf可以将输出写到变量中（给变量赋值）
        - 格式化支持的参数格式
            - c ascii字符
            - s 字符串
            - d 十进制整数
            - ld 十进制长整数
            - u  十进制无符号整数
            - lu 十进制无符号长整数
            - x 十六进制整数
            - lx 十六进制长整数
            - o 八进制整数
            - lo 八进制长整数
            - e e计数法表示浮点数
            - f 浮点数
            - g 选用e或f中较短的一种形式
        - 修饰符
            - \- 左对齐
            - \# 显示8进制整数时在前面加个0，显示16进制整数时在前面加个0x
            - \+ 显示使用d、e、f和g转换的整数时，加上正负号-、+
            - 0 用0而不是空白字符来填充所显示的值
        - 输出格式为：\%\-width.precision format\-specifier
            + width 指定宽度，未达到时填满, printf("\%\-20s","xxx")
            + precision 用于十进制或浮点数，控制小数点右边的数字位数， printf("%.2f",2.23432)
    - 内置函数
        - 字符串函数
            + sub(/reg/,newsubstr,str) 只替换第一个匹配字符串
            + gsub(/reg/,newsubstr,str) 将字符串str中所有符合/reg/正则的自传替换为字符串newsubstr
            + index(str,substr) 返回自传substr在串str中的索引
            + length(str) 返回字符串的长度
            + match(str,/reg/) 如果在串str中找到正则/reg/匹配的串，则返回出现的位置，未找到则返回0
            + split(str,array,sep) 使用分隔符sep吧字符串分解成数组array
            + substr(str,position\[,length\]) 返回str中从position开始的length个字符串
            + toupper(str) 对字符串进行大小写转换
            + sprintf("fmt",expr) 对expr使用printf格式说明
        - 算数函数
            + sin(x) 正弦函数
            + cos(x) 余弦函数
            + atan2(x,y) y，x范围内的余切
            + int(x) 取整，过程没有舍入
            + exp(x) 求幂
            + log(x) 自然对数
            + sqrt(x) 平方根
            + rand() 尝试一个大于0小于医德随机数
            + srand(x) x是rand()函数的种子

