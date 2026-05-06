"""
语义分析器 - 支持C语言子集
负责人：孟迁。
修改内容：优化四元式输出格式，增加更清晰的参数对齐
"""


from lexer import Lexer, Token, Position
from parser import Parser, ASTNode, ProgramNode, FunctionNode, BlockNode, \
                  VarDeclNode, AssignNode, IfNode, WhileNode, ForNode, \
                  ReturnNode, BinaryOpNode, UnaryOpNode, VarNode, LiteralNode, CallNode

class Symbol:
    """符号表项"""
    def __init__(self, name, symbol_type, scope_level=0, initialized=False, is_function=False, return_type=None, params=None):
        self.name = name
        self.type = symbol_type
        self.scope_level = scope_level
        self.initialized = initialized
        self.is_function = is_function
        self.return_type = return_type
        self.params = params or []  # 对于函数，存储参数类型列表

    def __str__(self):
        if self.is_function:
            params_str = ', '.join([f'{ptype} {pname}' for ptype, pname in self.params])
            return f"Function: {self.return_type} {self.name}({params_str})"
        else:
            status = "initialized" if self.initialized else "uninitialized"
            return f"Variable: {self.type} {self.name} ({status})"

class Quadruple:
    """四元式中间代码"""
    def __init__(self, op, arg1, arg2, result, position=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
        self.position = position or Position()

    def __str__(self):
        # 处理None值
        arg1_str = '' if self.arg1 is None else str(self.arg1)
        arg2_str = '' if self.arg2 is None else str(self.arg2)
        result_str = '' if self.result is None else str(self.result)

        return f'({self.op:10s}, {arg1_str:8s}, {arg2_str:8s}, {result_str:8s})'

class SemanticAnalyzer:
    """语义分析器"""

    def __init__(self):
        self.symbol_tables = [{}]  # 符号表栈
        self.current_scope = 0
        self.quads = []  # 四元式列表
        self.temp_count = 0
        self.label_count = 0
        self.errors = []
        self.current_function = None

    def new_temp(self):
        """生成新的临时变量"""
        temp_name = f't{self.temp_count}'
        self.temp_count += 1
        # 临时变量默认已初始化
        self.add_symbol(temp_name, 'temp', scope_level=self.current_scope, initialized=True)
        return temp_name

    def new_label(self):
        """生成新的标签"""
        label_name = f'L{self.label_count}'
        self.label_count += 1
        return label_name

    def add_symbol(self, name, symbol_type, scope_level=None, initialized=False, is_function=False, return_type=None, params=None):
        """添加符号到当前作用域"""
        if scope_level is None:
            scope_level = self.current_scope

        # 检查是否已存在（在同一作用域内）
        if scope_level < len(self.symbol_tables) and name in self.symbol_tables[scope_level]:
            # 允许函数重新声明（函数定义覆盖声明）
            if is_function and self.symbol_tables[scope_level][name].is_function:
                # 更新函数信息
                self.symbol_tables[scope_level][name] = Symbol(
                    name, symbol_type, scope_level, initialized,
                    is_function, return_type, params
                )
                return True
            else:
                self.error(f"Symbol '{name}' already defined in this scope")
                return False

        # 确保符号表栈足够大
        while len(self.symbol_tables) <= scope_level:
            self.symbol_tables.append({})

        symbol = Symbol(name, symbol_type, scope_level, initialized, is_function, return_type, params)
        self.symbol_tables[scope_level][name] = symbol
        return True

    def lookup_symbol(self, name, current_scope_only=False):
        """查找符号（从当前作用域向上查找）"""
        if current_scope_only:
            # 只在当前作用域查找
            if name in self.symbol_tables[self.current_scope]:
                return self.symbol_tables[self.current_scope][name]
            return None

        # 从当前作用域向上查找
        for i in range(self.current_scope, -1, -1):
            if name in self.symbol_tables[i]:
                return self.symbol_tables[i][name]

        return None

    def enter_scope(self):
        """进入新的作用域"""
        self.current_scope += 1
        if self.current_scope >= len(self.symbol_tables):
            self.symbol_tables.append({})

    def exit_scope(self):
        """退出当前作用域"""
        if self.current_scope > 0:
            self.current_scope -= 1

    def error(self, msg, position=None):
        """记录语义错误"""
        pos_str = f" at {position}" if position else ""
        error_msg = f"Semantic error{pos_str}: {msg}"
        self.errors.append(error_msg)
        print(f"⚠ {error_msg}")

    def warning(self, msg, position=None):
        """记录语义警告"""
        pos_str = f" at {position}" if position else ""
        warning_msg = f"Semantic warning{pos_str}: {msg}"
        print(f"⚠ {warning_msg}")

    def analyze(self, node):
        """分析AST"""
        try:
            # 第一阶段：收集所有函数声明
            self.collect_function_declarations(node)

            # 第二阶段：分析函数体
            self.visit(node)
            return self.quads, self.errors
        except Exception as e:
            self.error(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return self.quads, self.errors

    def collect_function_declarations(self, node):
        """收集所有函数声明（提前声明函数）"""
        if isinstance(node, ProgramNode):
            for func in node.functions:
                if isinstance(func, FunctionNode):
                    # 将函数添加到全局符号表
                    self.add_symbol(func.name, 'function', 0, True, True, func.return_type, func.params)

        # 添加内置函数
        self.add_symbol('print', 'function', 0, True, True, 'void', [])
        self.add_symbol('printf', 'function', 0, True, True, 'void', [])

    def visit(self, node):
        """访问节点"""
        if node is None:
            return None

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """通用访问方法"""
        self.error(f"No visitor for {type(node).__name__}")

    def visit_ProgramNode(self, node):
        """访问程序节点"""
        # 程序入口
        self.quads.append(Quadruple('PROG', 'START', None, None, Position(1, 1)))

        for func in node.functions:
            self.visit(func)

        # 程序结束
        self.quads.append(Quadruple('PROG', 'END', None, None, Position(1, 1)))

    def visit_FunctionNode(self, node):
        """访问函数节点"""
        # 保存当前函数
        old_function = self.current_function
        self.current_function = node.name

        # 生成函数入口标签
        self.quads.append(Quadruple('FUNC', node.name, None, None, node.position))

        # 进入函数作用域
        self.enter_scope()

        # 添加参数到符号表，并标记为已初始化
        for param_type, param_name in node.params:
            # 检查参数是否已在当前作用域定义
            existing_symbol = self.lookup_symbol(param_name, current_scope_only=True)
            if existing_symbol:
                self.error(f"Parameter '{param_name}' shadows existing symbol", node.position)
            else:
                self.add_symbol(param_name, param_type, self.current_scope, initialized=True)

        # 分析函数体
        self.visit(node.body)

        # 对于非void函数，确保有return语句
        if node.return_type != 'void' and node.name != 'main':
            # 检查是否有return语句
            has_return = False
            if isinstance(node.body, BlockNode):
                for stmt in node.body.statements:
                    if isinstance(stmt, ReturnNode):
                        has_return = True
                        break
            if not has_return:
                self.warning(f"Function '{node.name}' should return a value", node.position)
        elif node.return_type == 'void' and node.name != 'main':
            # void函数可以没有return
            pass

        # 退出函数作用域
        self.exit_scope()

        # 恢复当前函数
        self.current_function = old_function

        # 生成函数结束标签
        self.quads.append(Quadruple('ENDFUNC', None, None, None, node.position))

    def visit_BlockNode(self, node):
        """访问代码块节点"""
        self.enter_scope()

        for stmt in node.statements:
            self.visit(stmt)

        self.exit_scope()

    def visit_VarDeclNode(self, node):
        """访问变量声明节点"""
        for i, name in enumerate(node.names):
            # 添加到符号表
            initialized = (node.values[i] is not None)
            if not self.add_symbol(name, node.var_type, self.current_scope, initialized):
                continue

            # 如果有初始值，生成赋值四元式
            if node.values[i] is not None:
                # 分析表达式
                expr_result = self.visit(node.values[i])

                if expr_result:
                    # 生成赋值四元式
                    self.quads.append(Quadruple('=', expr_result, None, name, node.position))

    def visit_AssignNode(self, node):
        """访问赋值节点"""
        # 检查变量是否已声明
        symbol = self.lookup_symbol(node.var_name)
        if not symbol:
            self.error(f"Variable '{node.var_name}' not declared", node.position)
            return None

        # 分析表达式
        expr_result = self.visit(node.expr)

        if expr_result:
            # 生成赋值四元式
            self.quads.append(Quadruple('=', expr_result, None, node.var_name, node.position))

            # 标记变量已初始化
            symbol.initialized = True

            return node.var_name

        return None

    def visit_IfNode(self, node):
        """访问if语句节点"""
        # 生成标签
        else_label = self.new_label()
        end_label = self.new_label()

        # 分析条件表达式
        cond_result = self.visit(node.condition)

        # 生成条件跳转
        if cond_result:
            self.quads.append(Quadruple('IF_FALSE', cond_result, None, else_label, node.position))

        # 分析then块
        self.visit(node.then_block)

        # 跳转到结束标签
        if node.else_block:
            self.quads.append(Quadruple('GOTO', None, None, end_label, node.position))

        # else标签
        if node.else_block:
            self.quads.append(Quadruple('LABEL', else_label, None, None, node.position))

            # 分析else块
            self.visit(node.else_block)

            # 结束标签
            self.quads.append(Quadruple('LABEL', end_label, None, None, node.position))
        else:
            # 如果没有else，else_label就是结束标签
            self.quads.append(Quadruple('LABEL', else_label, None, None, node.position))

    def visit_WhileNode(self, node):
        """访问while循环节点"""
        # 生成标签
        start_label = self.new_label()
        end_label = self.new_label()

        # 开始标签
        self.quads.append(Quadruple('LABEL', start_label, None, None, node.position))

        # 分析条件表达式
        cond_result = self.visit(node.condition)

        # 生成条件跳转
        if cond_result:
            self.quads.append(Quadruple('IF_FALSE', cond_result, None, end_label, node.position))

        # 分析循环体
        self.visit(node.body)

        # 跳回开始
        self.quads.append(Quadruple('GOTO', None, None, start_label, node.position))

        # 结束标签
        self.quads.append(Quadruple('LABEL', end_label, None, None, node.position))

    def visit_ForNode(self, node):
        """访问for循环节点"""
        # 生成标签
        start_label = self.new_label()
        end_label = self.new_label()

        # 分析初始化部分
        if node.init:
            self.visit(node.init)

        # 开始标签
        self.quads.append(Quadruple('LABEL', start_label, None, None, node.position))

        # 分析条件部分
        if node.condition:
            cond_result = self.visit(node.condition)
            if cond_result:
                self.quads.append(Quadruple('IF_FALSE', cond_result, None, end_label, node.position))

        # 分析循环体
        self.visit(node.body)

        # 分析更新部分
        if node.update:
            self.visit(node.update)

        # 跳回开始
        self.quads.append(Quadruple('GOTO', None, None, start_label, node.position))

        # 结束标签
        self.quads.append(Quadruple('LABEL', end_label, None, None, node.position))

    def visit_ReturnNode(self, node):
        """访问return节点"""
        if node.expr:
            expr_result = self.visit(node.expr)
            self.quads.append(Quadruple('RET', expr_result, None, None, node.position))
        else:
            self.quads.append(Quadruple('RET', None, None, None, node.position))

    def visit_BinaryOpNode(self, node):
        """访问二元运算节点"""
        left_result = self.visit(node.left)
        right_result = self.visit(node.right)

        if left_result and right_result:
            # 生成临时变量
            temp_var = self.new_temp()

            # 生成运算四元式
            op_map = {
                '+': 'ADD',
                '-': 'SUB',
                '*': 'MUL',
                '/': 'DIV',
                '%': 'MOD',
                '==': 'EQ',
                '!=': 'NE',
                '<': 'LT',
                '>': 'GT',
                '<=': 'LE',
                '>=': 'GE',
                '&&': 'AND',
                '||': 'OR',
            }

            quad_op = op_map.get(node.op, node.op)
            self.quads.append(Quadruple(quad_op, left_result, right_result, temp_var, node.position))

            return temp_var

        return None

    def visit_UnaryOpNode(self, node):
        """访问一元运算节点"""
        expr_result = self.visit(node.expr)

        if expr_result:
            # 生成临时变量
            temp_var = self.new_temp()

            # 生成运算四元式
            op_map = {
                '!': 'NOT',
                '-': 'NEG',
                '++': 'INC',
                '--': 'DEC',
            }

            quad_op = op_map.get(node.op, node.op)
            self.quads.append(Quadruple(quad_op, expr_result, None, temp_var, node.position))

            return temp_var

        return None

    def visit_VarNode(self, node):
        """访问变量节点"""
        symbol = self.lookup_symbol(node.name)
        if not symbol:
            self.error(f"Variable '{node.name}' not declared", node.position)
            return None

        return node.name

    def visit_LiteralNode(self, node):
        """访问字面量节点"""
        # 生成临时变量存储字面量
        temp_var = self.new_temp()

        # 根据类型生成不同的赋值
        if node.type == 'string':
            # 字符串字面量
            self.quads.append(Quadruple('STRING', node.value, None, temp_var, node.position))
        else:
            # 其他字面量
            self.quads.append(Quadruple('=', node.value, None, temp_var, node.position))

        return temp_var

    def visit_CallNode(self, node):
        """访问函数调用节点"""
        # 检查函数是否存在
        symbol = self.lookup_symbol(node.name)

        if not symbol or not symbol.is_function:
            # 如果是未声明的函数调用，报错
            if node.name not in ['print', 'printf']:
                self.error(f"Function '{node.name}' not declared", node.position)
                return None

        # 分析参数
        arg_results = []
        for arg in node.args:
            arg_result = self.visit(arg)
            if arg_result:
                arg_results.append(arg_result)

        # 生成调用四元式
        if node.name == 'print':
            for arg in arg_results:
                self.quads.append(Quadruple('PRINT', arg, None, None, node.position))
        elif node.name == 'printf':
            # printf的第一个参数是格式字符串
            if arg_results:
                format_str = arg_results[0]
                # 传递格式字符串和后续参数
                if len(arg_results) > 1:
                    # 对于有参数的printf
                    for i in range(1, len(arg_results)):
                        self.quads.append(Quadruple('PRINTF', format_str, arg_results[i], f'arg{i}', node.position))
                else:
                    # 对于无参数的printf
                    self.quads.append(Quadruple('PRINT', format_str, None, None, node.position))
        else:
            # 普通函数调用
            for i, arg in enumerate(arg_results):
                self.quads.append(Quadruple('PARAM', arg, None, f'arg{i}', node.position))

            # 生成调用
            temp_var = self.new_temp()
            self.quads.append(Quadruple('CALL', node.name, len(arg_results), temp_var, node.position))

            return temp_var

        return None

def test_semantic():
    """测试语义分析器"""
    code = """
    int main() {
        int a = 10;
        int b = 20;
        int sum = a + b * 2;
        
        if (sum > 30) {
            print("Sum is large");
        } else {
            print("Sum is small");
        }
        
        int i = 0;
        while (i < 10) {
            i = i + 1;
        }
        
        return 0;
    }
    """

    print("源代码:")
    print(code)
    print("=" * 60)

    # 词法分析
    lexer = Lexer(code)

    # 语法分析
    parser = Parser(lexer)
    ast = parser.parse()

    if ast:
        print("语义分析和中间代码生成:")
        print("-" * 60)

        # 语义分析
        analyzer = SemanticAnalyzer()
        quads, errors = analyzer.analyze(ast)

        # 输出中间代码
        print("四元式中间代码:")
        print("(操作符,      操作数1,   操作数2,   结果)")
        print("-" * 60)
        for i, quad in enumerate(quads):
            print(f"{i:3d}: {quad}")

        print()

        # 输出符号表
        print("符号表:")
        print("-" * 60)
        for scope_level, symbols in enumerate(analyzer.symbol_tables):
            if symbols:
                print(f"Scope {scope_level}:")
                for name, symbol in symbols.items():
                    print(f"  {symbol}")

        print()

        # 输出错误
        if errors:
            print(f"语义分析完成，发现 {len(errors)} 个错误:")
            for error in errors:
                print(f"  {error}")
        else:
            print("✓ 语义分析成功，无错误!")

if __name__ == '__main__':
    test_semantic()
