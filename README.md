# SDUT-IT项目管理实验仓库

#### 介绍
这是使用python语言编写的SDUT编译原理项目

#### 软件架构
软件架构说明：
1.src：项目源代码
lexer.py：词法分析器
parser.py：语法分析器
semantic.py：语义分析器
compiler.py：编辑器主程序
2.tests：测试用c语言子集程序
test_arithmetic.c：基本算数运算程序
test_condition.c：条件语句程序
test_loop.c：循环语句程序
test_simple.c：完整测试程序
3.output:编辑器主程序编译结果输出
tokens.txt：Token列表
quads.txt：四元式


#### 使用说明

1.  可以分别使用lexer.py/parser.py/semantic.py对测试程序进行词法/语法/语义分析
	运行命令：python src/xxxx.py xxxx.c
2.  使用compiler.py对测试c语言子集程序进行编译并输出编译结果
	运行命令：python src/compiler.py xxxx.c
	
#### 参与贡献
孔维正、王铭昌、孟迁

