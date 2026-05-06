"""
扩展的语法分析器 - 支持C语言子集
"""

from lexer import Lexer, Token, Position

class ASTNode:
    """AST节点基类"""
    def __init__(self, position=None):
        self.position = position or Position()
        self.children = []

    def add_child(self, node):
        if node:
            self.children.append(node)

    def __str__(self):
        return self.__class__.__name__

class ProgramNode(ASTNode):
    """程序节点"""
    def __init__(self, functions, position=None):
        super().__init__(position)
        self.functions = functions or []
        for func in self.functions:
            self.add_child(func)

    def __str__(self):
        return f"Program({len(self.functions)} functions)"

class FunctionNode(ASTNode):
    """函数节点"""
    def __init__(self, name, return_type, params, body, position=None):
        super().__init__(position)
        self.name = name
        self.return_type = return_type
        self.params = params or []
        self.body = body
        self.add_child(body)

    def __str__(self):
        return f"Function({self.return_type} {self.name})"

class BlockNode(ASTNode):
    """代码块节点"""
    def __init__(self, statements, position=None):
        super().__init__(position)
        self.statements = statements or []
        for stmt in self.statements:
            self.add_child(stmt)

    def __str__(self):
        return f"Block({len(self.statements)} statements)"

class VarDeclNode(ASTNode):
    """变量声明节点"""
    def __init__(self, var_type, names, values=None, position=None):
        super().__init__(position)
        self.var_type = var_type
        self.names = names or []
        self.values = values or [None] * len(names)

    def __str__(self):
        return f"VarDecl({self.var_type} {', '.join(self.names)})"

class AssignNode(ASTNode):
    """赋值节点"""
    def __init__(self, var_name, expr, position=None):
        super().__init__(position)
        self.var_name = var_name
        self.expr = expr
        self.add_child(expr)

    def __str__(self):
        return f"Assign({self.var_name})"

class IfNode(ASTNode):
    """if语句节点"""
    def __init__(self, condition, then_block, else_block=None, position=None):
        super().__init__(position)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.add_child(condition)
        self.add_child(then_block)
        if else_block:
            self.add_child(else_block)

    def __str__(self):
        return f"If"

class WhileNode(ASTNode):
    """while循环节点"""
    def __init__(self, condition, body, position=None):
        super().__init__(position)
        self.condition = condition
        self.body = body
        self.add_child(condition)
        self.add_child(body)

    def __str__(self):
        return f"While"

class ForNode(ASTNode):
    """for循环节点"""
    def __init__(self, init, condition, update, body, position=None):
        super().__init__(position)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
        if init:
            self.add_child(init)
        self.add_child(condition)
        if update:
            self.add_child(update)
        self.add_child(body)

    def __str__(self):
        return f"For"

class ReturnNode(ASTNode):
    """return语句节点"""
    def __init__(self, expr=None, position=None):
        super().__init__(position)
        self.expr = expr
        if expr:
            self.add_child(expr)

    def __str__(self):
        return f"Return"

class BinaryOpNode(ASTNode):
    """二元运算节点"""
    def __init__(self, left, op, right, position=None):
        super().__init__(position)
        self.left = left
        self.op = op
        self.right = right
        self.add_child(left)
        self.add_child(right)

    def __str__(self):
        return f"BinaryOp({self.op})"

class UnaryOpNode(ASTNode):
    """一元运算节点"""
    def __init__(self, op, expr, position=None):
        super().__init__(position)
        self.op = op
        self.expr = expr
        self.add_child(expr)

    def __str__(self):
        return f"UnaryOp({self.op})"

class VarNode(ASTNode):
    """变量节点"""
    def __init__(self, name, position=None):
        super().__init__(position)
        self.name = name

    def __str__(self):
        return f"Var({self.name})"

class LiteralNode(ASTNode):
    """字面量节点"""
    def __init__(self, value, type_, position=None):
        super().__init__(position)
        self.value = value
        self.type = type_

    def __str__(self):
        return f"Literal({self.type}: {self.value})"

class CallNode(ASTNode):
    """函数调用节点"""
    def __init__(self, name, args, position=None):
        super().__init__(position)
        self.name = name
        self.args = args or []
        for arg in self.args:
            self.add_child(arg)

    def __str__(self):
        return f"Call({self.name})"

class Parser:
    """语法分析器"""

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.errors = []

    def error(self, msg, token=None):
        """语法错误处理"""
        if token:
            pos = token.position
            msg = f"Syntax error at {pos}: {msg}"
        else:
            pos = self.current_token.position
            msg = f"Syntax error at {pos}: {msg}"

        self.errors.append(msg)
        raise Exception(msg)

    def eat(self, token_type):
        """消费当前token"""
        if self.current_token.type == token_type:
            token = self.current_token
            self.current_token = self.lexer.get_next_token()
            return token
        else:
            expected = token_type
            got = f"{self.current_token.type} '{self.current_token.value}'"
            self.error(f"Expected {expected}, got {got}", self.current_token)

    def parse(self):
        """解析程序"""
        try:
            program = self.parse_program()
            return program
        except Exception as e:
            print(f"Parsing failed at token {self.current_token}: {e}")
            return None

    def parse_program(self):
        """解析程序：函数定义列表"""
        functions = []

        while self.current_token.type != 'EOF':
            if self.current_token.type in ('INT', 'FLOAT', 'CHAR', 'VOID', 'BOOL'):
                func = self.parse_function()
                if func:
                    functions.append(func)
            else:
                # 跳过无法识别的token，尝试恢复
                print(f"Warning: Unexpected token at program level: {self.current_token.type} '{self.current_token.value}'")
                self.eat(self.current_token.type)  # 跳过这个token

        return ProgramNode(functions, Position(1, 1))

    def parse_function(self):
        """解析函数定义"""
        # 返回类型
        return_type = self.current_token.value
        self.eat(self.current_token.type)

        # 函数名
        if self.current_token.type != 'IDENTIFIER':
            self.error("Expected function name")
        func_name = self.current_token.value
        self.eat('IDENTIFIER')

        # 参数列表
        self.eat('LPAREN')
        params = self.parse_params()
        self.eat('RPAREN')

        # 函数体
        body = self.parse_block()

        return FunctionNode(func_name, return_type, params, body)

    def parse_params(self):
        """解析参数列表"""
        params = []

        if self.current_token.type != 'RPAREN':
            # 解析第一个参数
            if self.current_token.type not in ('INT', 'FLOAT', 'CHAR', 'BOOL'):
                # 允许无参数或void参数
                if self.current_token.type == 'VOID':
                    self.eat('VOID')
                    return params
                else:
                    self.error("Expected parameter type")

            param_type = self.current_token.value
            self.eat(self.current_token.type)

            if self.current_token.type != 'IDENTIFIER':
                self.error("Expected parameter name")
            param_name = self.current_token.value
            self.eat('IDENTIFIER')

            params.append((param_type, param_name))

            # 解析更多参数
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')

                if self.current_token.type not in ('INT', 'FLOAT', 'CHAR', 'BOOL'):
                    self.error("Expected parameter type")
                param_type = self.current_token.value
                self.eat(self.current_token.type)

                if self.current_token.type != 'IDENTIFIER':
                    self.error("Expected parameter name")
                param_name = self.current_token.value
                self.eat('IDENTIFIER')

                params.append((param_type, param_name))

        return params

    def parse_block(self):
        """解析代码块"""
        self.eat('LBRACE')
        statements = []

        while self.current_token.type != 'RBRACE' and self.current_token.type != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        self.eat('RBRACE')
        return BlockNode(statements)

    def parse_statement(self):
        """解析语句"""
        token_type = self.current_token.type

        if token_type in ('INT', 'FLOAT', 'CHAR', 'BOOL'):
            return self.parse_var_declaration()
        elif token_type == 'IDENTIFIER':
            # 使用peek_token查看下一个token
            next_token = self.lexer.peek_token()

            if next_token.type == 'LPAREN':
                # 函数调用
                return self.parse_function_call_statement()
            elif next_token.type == 'ASSIGN':
                # 赋值
                return self.parse_assignment()
            else:
                self.error(f"Unexpected token after identifier: {next_token.type}")
        elif token_type == 'IF':
            return self.parse_if_statement()
        elif token_type == 'WHILE':
            return self.parse_while_statement()
        elif token_type == 'FOR':
            return self.parse_for_statement()
        elif token_type == 'RETURN':
            return self.parse_return_statement()
        elif token_type in ('PRINT', 'PRINTF'):  # 关键修改：同时处理PRINT和PRINTF
            return self.parse_print_statement()
        elif token_type == 'LBRACE':
            return self.parse_block()
        elif token_type == 'SEMICOLON':
            # 空语句
            self.eat('SEMICOLON')
            return None
        else:
            self.error(f"Unexpected token in statement: {token_type}")

    def parse_var_declaration(self):
        """解析变量声明"""
        var_type = self.current_token.value
        self.eat(self.current_token.type)

        names = []
        values = []

        # 解析第一个变量
        if self.current_token.type != 'IDENTIFIER':
            self.error("Expected variable name")
        name = self.current_token.value
        self.eat('IDENTIFIER')
        names.append(name)

        # 检查是否有初始化
        if self.current_token.type == 'ASSIGN':
            self.eat('ASSIGN')
            value = self.parse_expression()
            values.append(value)
        else:
            values.append(None)

        # 解析更多变量
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')

            if self.current_token.type != 'IDENTIFIER':
                self.error("Expected variable name")
            name = self.current_token.value
            self.eat('IDENTIFIER')
            names.append(name)

            if self.current_token.type == 'ASSIGN':
                self.eat('ASSIGN')
                value = self.parse_expression()
                values.append(value)
            else:
                values.append(None)

        self.eat('SEMICOLON')
        return VarDeclNode(var_type, names, values)

    def parse_assignment(self):
        """解析赋值语句"""
        var_name = self.current_token.value
        self.eat('IDENTIFIER')

        self.eat('ASSIGN')
        expr = self.parse_expression()

        self.eat('SEMICOLON')
        return AssignNode(var_name, expr)

    def parse_if_statement(self):
        """解析if语句"""
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.parse_expression()
        self.eat('RPAREN')

        then_block = self.parse_block_or_statement()

        # 检查是否有else
        else_block = None
        if self.current_token.type == 'ELSE':
            self.eat('ELSE')
            else_block = self.parse_block_or_statement()

        return IfNode(condition, then_block, else_block)

    def parse_block_or_statement(self):
        """解析代码块或单条语句"""
        if self.current_token.type == 'LBRACE':
            return self.parse_block()
        else:
            # 单条语句
            return BlockNode([self.parse_statement()])

    def parse_while_statement(self):
        """解析while循环"""
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.parse_expression()
        self.eat('RPAREN')

        body = self.parse_block_or_statement()
        return WhileNode(condition, body)

    def parse_for_statement(self):
        """解析for循环"""
        self.eat('FOR')
        self.eat('LPAREN')

        # 初始化部分
        init = None
        if self.current_token.type != 'SEMICOLON':
            init = self.parse_expression()
        self.eat('SEMICOLON')

        # 条件部分
        condition = None
        if self.current_token.type != 'SEMICOLON':
            condition = self.parse_expression()
        self.eat('SEMICOLON')

        # 更新部分
        update = None
        if self.current_token.type != 'RPAREN':
            update = self.parse_expression()
        self.eat('RPAREN')

        body = self.parse_block_or_statement()
        return ForNode(init, condition, update, body)

    def parse_return_statement(self):
        """解析return语句"""
        self.eat('RETURN')

        expr = None
        if self.current_token.type != 'SEMICOLON':
            expr = self.parse_expression()

        self.eat('SEMICOLON')
        return ReturnNode(expr)

    def parse_print_statement(self):
        """解析print/printf语句"""
        func_name = self.current_token.value
        position = self.current_token.position

        if func_name == 'print':
            self.eat('PRINT')

            # 检查是否有括号
            has_paren = False
            if self.current_token.type == 'LPAREN':
                has_paren = True
                self.eat('LPAREN')

            expr = self.parse_expression()

            if has_paren:
                self.eat('RPAREN')

            self.eat('SEMICOLON')
            return CallNode('print', [expr], position)

        elif func_name == 'printf':
            self.eat('PRINTF')
            self.eat('LPAREN')

            # 第一个参数必须是字符串
            if self.current_token.type != 'STRING':
                self.error("Expected format string in printf")
            format_str = self.current_token.value
            self.eat('STRING')

            args = [LiteralNode(format_str, 'string', position)]

            # 解析可选参数
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                expr = self.parse_expression()
                args.append(expr)

            self.eat('RPAREN')
            self.eat('SEMICOLON')

            return CallNode('printf', args, position)
        else:
            self.error(f"Unknown print function: {func_name}")

    def parse_function_call_statement(self):
        """解析函数调用语句"""
        func_name = self.current_token.value
        position = self.current_token.position
        self.eat('IDENTIFIER')

        self.eat('LPAREN')
        args = self.parse_args()
        self.eat('RPAREN')

        self.eat('SEMICOLON')
        return CallNode(func_name, args, position)

    def parse_function_call_expression(self, func_name, position):
        """解析函数调用表达式（作为表达式的一部分）"""
        self.eat('LPAREN')
        args = self.parse_args()
        self.eat('RPAREN')
        return CallNode(func_name, args, position)

    def parse_args(self):
        """解析参数列表"""
        args = []

        if self.current_token.type != 'RPAREN':
            args.append(self.parse_expression())

            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                args.append(self.parse_expression())

        return args

    def parse_expression(self):
        """解析表达式"""
        return self.parse_logical_or()

    def parse_logical_or(self):
        """解析逻辑或"""
        node = self.parse_logical_and()

        while self.current_token.type == 'OR':
            op_token = self.current_token
            self.eat('OR')
            right = self.parse_logical_and()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_logical_and(self):
        """解析逻辑与"""
        node = self.parse_equality()

        while self.current_token.type == 'AND':
            op_token = self.current_token
            self.eat('AND')
            right = self.parse_equality()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_equality(self):
        """解析相等性比较"""
        node = self.parse_relational()

        while self.current_token.type in ('EQ', 'NEQ'):
            op_token = self.current_token
            self.eat(self.current_token.type)
            right = self.parse_relational()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_relational(self):
        """解析关系比较"""
        node = self.parse_additive()

        while self.current_token.type in ('LT', 'GT', 'LE', 'GE'):
            op_token = self.current_token
            self.eat(self.current_token.type)
            right = self.parse_additive()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_additive(self):
        """解析加减法"""
        node = self.parse_multiplicative()

        while self.current_token.type in ('PLUS', 'MINUS'):
            op_token = self.current_token
            self.eat(self.current_token.type)
            right = self.parse_multiplicative()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_multiplicative(self):
        """解析乘除法"""
        node = self.parse_unary()

        while self.current_token.type in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            op_token = self.current_token
            self.eat(self.current_token.type)
            right = self.parse_unary()
            node = BinaryOpNode(node, op_token.value, right)

        return node

    def parse_unary(self):
        """解析一元运算符"""
        if self.current_token.type in ('NOT', 'MINUS', 'INCREMENT', 'DECREMENT'):
            op_token = self.current_token
            self.eat(self.current_token.type)
            expr = self.parse_unary()
            return UnaryOpNode(op_token.value, expr)

        return self.parse_primary()

    def parse_primary(self):
        """解析基本表达式"""
        token = self.current_token

        if token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')

            # 检查是否是函数调用
            if self.current_token.type == 'LPAREN':
                # 这是函数调用
                return self.parse_function_call_expression(token.value, token.position)
            else:
                # 这是变量引用
                return VarNode(token.value, token.position)

        elif token.type == 'INTEGER':
            self.eat('INTEGER')
            return LiteralNode(token.value, 'int', token.position)

        elif token.type == 'FLOAT':
            self.eat('FLOAT')
            return LiteralNode(token.value, 'float', token.position)

        elif token.type == 'STRING':
            self.eat('STRING')
            return LiteralNode(token.value, 'string', token.position)

        elif token.type == 'CHAR':
            self.eat('CHAR')
            return LiteralNode(token.value, 'char', token.position)

        elif token.type == 'TRUE':
            self.eat('TRUE')
            return LiteralNode(True, 'bool', token.position)

        elif token.type == 'FALSE':
            self.eat('FALSE')
            return LiteralNode(False, 'bool', token.position)

        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr

        else:
            self.error(f"Unexpected token in expression: {token.type}")

def print_ast(node, indent=0):
    """打印AST"""
    if node is None:
        return

    indent_str = '  ' * indent
    print(f"{indent_str}{node}")

    # 特殊处理某些节点
    if isinstance(node, ProgramNode):
        for func in node.functions:
            print_ast(func, indent + 1)

    elif isinstance(node, FunctionNode):
        print_ast(node.body, indent + 1)

    elif isinstance(node, BlockNode):
        for stmt in node.statements:
            print_ast(stmt, indent + 1)

    elif isinstance(node, VarDeclNode):
        pass  # 已经在__str__中显示

    else:
        for child in node.children:
            print_ast(child, indent + 1)

def test_parser():
    """测试语法分析器"""
    code = """
    int main() {
        int a = 10;
        int b = 20;
        int sum = a + b * 2;
        
        if (sum > 30) {
            printf("Sum is large");
        } else {
            printf("Sum is small");
        }
        
        int i = 0;
        while (i < 10) {
            i = i + 1;
        }
        
        return 0;
    }
    """

    lexer = Lexer(code)
    parser = Parser(lexer)

    print("开始语法分析...")
    ast = parser.parse()

    if ast:
        print("AST结构:")
        print_ast(ast)

if __name__ == '__main__':
    test_parser()