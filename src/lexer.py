"""
扩展的词法分析器 - 支持C语言子集
负责人：王铭昌
修改内容：添加debug关键字
"""

class Position:
    """位置信息"""
    def __init__(self, line=1, column=1):
        self.line = line
        self.column = column

    def __str__(self):
        return f"line {self.line}, column {self.column}"

    def copy(self):
        return Position(self.line, self.column)

class Token:
    """Token类"""
    def __init__(self, type_, value, position=None):
        self.type = type_      # Token类型
        self.value = value     # Token值
        self.position = position or Position()

    def __str__(self):
        return f"Token({self.type}, '{self.value}', {self.position})"

    def __repr__(self):
        return self.__str__()

class Lexer:
    """扩展的词法分析器"""

    # 关键字
    KEYWORDS = {
        'int': 'INT',
        'float': 'FLOAT',
        'char': 'CHAR',
        'void': 'VOID',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'return': 'RETURN',
        'print': 'PRINT',
        'printf': 'PRINTF',  # 添加printf支持
        'read': 'READ',
        'true': 'TRUE',
        'false': 'FALSE',
        'bool': 'BOOL',
    }

    # 运算符
    OPERATORS = {
        '=': 'ASSIGN',
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'MULTIPLY',
        '/': 'DIVIDE',
        '%': 'MODULO',
        '==': 'EQ',
        '!=': 'NEQ',
        '<': 'LT',
        '>': 'GT',
        '<=': 'LE',
        '>=': 'GE',
        '&&': 'AND',
        '||': 'OR',
        '!': 'NOT',
        '++': 'INCREMENT',
        '--': 'DECREMENT',
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None

    def error(self, msg):
        """错误处理"""
        raise Exception(f'Lexical error at line {self.line}, column {self.column}: {msg}')

    def advance(self):
        """前进一个字符"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self, n=1):
        """查看前向字符"""
        peek_pos = self.pos + n
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def peek_token(self):
        """查看下一个token但不消费它"""
        # 保存当前状态
        saved_pos = self.pos
        saved_line = self.line
        saved_column = self.column
        saved_current_char = self.current_char

        # 获取下一个token
        next_token = self.get_next_token()

        # 恢复状态
        self.pos = saved_pos
        self.line = saved_line
        self.column = saved_column
        self.current_char = saved_current_char

        return next_token

    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """跳过注释"""
        # 单行注释 //
        if self.current_char == '/' and self.peek() == '/':
            self.advance()  # 跳过 /
            self.advance()  # 跳过 /
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()
        # 多行注释 /* */
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()  # 跳过 /
            self.advance()  # 跳过 *
            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # 跳过 *
                    self.advance()  # 跳过 /
                    break
                self.advance()
            else:
                self.error("Unterminated comment")
        else:
            self.error("Expected comment")

    def number(self):
        """读取数字"""
        start_pos = Position(self.line, self.column)
        result = ''
        is_float = False

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    self.error("Invalid float number")
                is_float = True
            result += self.current_char
            self.advance()

        # 科学计数法支持（可选）
        if self.current_char in ('e', 'E'):
            result += self.current_char
            self.advance()
            if self.current_char in ('+', '-'):
                result += self.current_char
                self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            is_float = True

        if is_float:
            return Token('FLOAT', float(result), start_pos)
        else:
            return Token('INTEGER', int(result), start_pos)

    def identifier(self):
        """读取标识符或关键字"""
        start_pos = Position(self.line, self.column)
        result = ''

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # 检查是否是关键字
        token_type = self.KEYWORDS.get(result, 'IDENTIFIER')
        return Token(token_type, result, start_pos)

    def string(self):
        """读取字符串"""
        start_pos = Position(self.line, self.column)
        result = ''
        self.advance()  # 跳过开始的引号

        while self.current_char is not None and self.current_char != '"':
            # 处理转义字符
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == '\\':
                    result += '\\'
                else:
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            self.advance()

        if self.current_char != '"':
            self.error("Unterminated string")

        self.advance()  # 跳过结束的引号
        return Token('STRING', result, start_pos)

    def char(self):
        """读取字符"""
        start_pos = Position(self.line, self.column)
        self.advance()  # 跳过开始的单引号

        if self.current_char == '\\':
            self.advance()
            if self.current_char == 'n':
                value = '\n'
            elif self.current_token == 't':
                value = '\t'
            elif self.current_char == "'":
                value = "'"
            elif self.current_char == '\\':
                value = '\\'
            else:
                self.error("Invalid escape character")
        else:
            value = self.current_char
            self.advance()

        if self.current_char != "'":
            self.error("Unterminated character")

        self.advance()  # 跳过结束的单引号
        return Token('CHAR', value, start_pos)

    def get_next_token(self):
        """获取下一个Token"""
        while self.current_char is not None:
            # 跳过空白
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # 处理注释
            if self.current_char == '/':
                next_char = self.peek()
                if next_char in ('/', '*'):
                    self.skip_comment()
                    continue

            # 数字
            if self.current_char.isdigit() or (self.current_char == '.' and self.peek() is not None and self.peek().isdigit()):
                return self.number()

            # 标识符或关键字
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            # 字符串
            if self.current_char == '"':
                return self.string()

            # 字符
            if self.current_char == "'":
                return self.char()

            # 运算符
            if self.current_char in self.OPERATORS:
                # 检查双字符运算符
                two_char_op = self.current_char + (self.peek() or '')
                if two_char_op in self.OPERATORS:
                    op = two_char_op
                    token_type = self.OPERATORS[op]
                    pos = Position(self.line, self.column)
                    self.advance()
                    self.advance()
                    return Token(token_type, op, pos)

                # 单字符运算符
                op = self.current_char
                token_type = self.OPERATORS[op]
                pos = Position(self.line, self.column)
                self.advance()
                return Token(token_type, op, pos)

            # 分隔符
            if self.current_char == ';':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('SEMICOLON', ';', pos)

            if self.current_char == ',':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('COMMA', ',', pos)

            if self.current_char == '(':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('LPAREN', '(', pos)

            if self.current_char == ')':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('RPAREN', ')', pos)

            if self.current_char == '{':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('LBRACE', '{', pos)

            if self.current_char == '}':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('RBRACE', '}', pos)

            if self.current_char == '[':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('LBRACKET', '[', pos)

            if self.current_char == ']':
                pos = Position(self.line, self.column)
                self.advance()
                return Token('RBRACKET', ']', pos)

            # 未知字符
            self.error(f"Unexpected character: '{self.current_char}'")

        return Token('EOF', None, Position(self.line, self.column))

    def tokenize(self):
        """获取所有Token"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens

def test_lexer():
    """测试词法分析器"""
    code = """
    // 测试程序
    int main() {
        int a = 10;
        int b = 20;
        int sum = a + b * 2;
        if (sum > 20) {
            printf("Sum is greater than 20");
        }
        return 0;
    }
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()

    print("Token列表:")
    for token in tokens:
        if token.type != 'EOF':
            print(f"  {token.type:12s} '{token.value}'")

if __name__ == '__main__':
    test_lexer()
