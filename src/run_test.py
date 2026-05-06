"""
测试编译器 - 避免文件覆盖问题
"""

import sys
import os
import time

# 确保可以导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def compile_and_save(source_code, filename="test", output_dir="output"):
    """编译并保存结果，使用时间戳避免覆盖"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    print("=" * 70)
    print(f"编译文件: {filename}")
    print("=" * 70)

    # 词法分析
    print("\n[阶段1] 词法分析")
    print("-" * 40)
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # 显示Tokens
    display_tokens = [t for t in tokens if t.type != 'EOF']
    print(f"识别到 {len(display_tokens)} 个Token")

    if len(display_tokens) > 0:
        print("前20个Token:")
        for i, token in enumerate(display_tokens[:20]):
            print(f"  [{i:2d}] {token.type:12s} '{token.value}'")
        if len(display_tokens) > 20:
            print(f"  ... 还有 {len(display_tokens) - 20} 个Token")

    # 保存Token列表
    token_file = os.path.join(output_dir, f"{filename}_{timestamp}_tokens.txt")
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("Token列表:\n")
        f.write("=" * 60 + "\n")
        for i, token in enumerate(tokens):
            if token.type != 'EOF':
                f.write(f"[{i:3d}] {token.type:12s} '{token.value}'\n")

    # 语法分析
    print("\n[阶段2] 语法分析")
    print("-" * 40)
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()

    if ast:
        print("✓ 语法分析成功")
    else:
        print("✗ 语法分析失败")
        return False

    # 语义分析和中间代码生成
    print("\n[阶段3] 语义分析和中间代码生成")
    print("-" * 40)
    analyzer = SemanticAnalyzer()
    quads, errors = analyzer.analyze(ast)

    if errors:
        print(f"发现 {len(errors)} 个语义错误")
    else:
        print("✓ 语义分析成功")

    # 输出中间代码
    print(f"\n生成的中间代码 ({len(quads)} 个四元式):")
    print("=" * 70)
    print("序号 | 操作符        | 操作数1   | 操作数2   | 结果")
    print("-" * 70)

    for i, quad in enumerate(quads):
        print(f"{i:3d} | {quad}")

    # 保存四元式
    quad_file = os.path.join(output_dir, f"{filename}_{timestamp}_quads.txt")
    with open(quad_file, "w", encoding="utf-8") as f:
        f.write("四元式中间代码:\n")
        f.write("=" * 60 + "\n")
        f.write("序号 | 操作符        | 操作数1   | 操作数2   | 结果\n")
        f.write("-" * 60 + "\n")
        for i, quad in enumerate(quads):
            f.write(f"{i:3d} | {quad}\n")

    # 保存错误信息
    if errors:
        error_file = os.path.join(output_dir, f"{filename}_{timestamp}_errors.txt")
        with open(error_file, "w", encoding="utf-8") as f:
            f.write("编译错误:\n")
            f.write("=" * 60 + "\n")
            for error in errors:
                f.write(f"{error}\n")

    # 输出总结
    print("\n" + "=" * 70)
    print("编译结果:")
    if errors:
        print(f"✗ 编译完成，但有 {len(errors)} 个错误")
        for error in errors[:5]:
            print(f"  {error}")
        if len(errors) > 5:
            print(f"  ... 还有 {len(errors) - 5} 个错误")
    else:
        print("✓ 编译成功完成!")
    print("=" * 70)

    print(f"\n结果已保存到:")
    print(f"  Token列表: {token_file}")
    print(f"  四元式: {quad_file}")
    if errors:
        print(f"  错误信息: {error_file}")

    return len(errors) == 0


def test_from_file(filename):
    """从文件测试"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()

        base_name = os.path.splitext(os.path.basename(filename))[0]
        return compile_and_save(source_code, base_name)
    except FileNotFoundError:
        print(f"错误: 文件 '{filename}' 不存在")
        return False


def test_simple():
    """测试简单程序"""
    source_code = """
    int main() {
        int a = 5, b = 10, c;
        float f = 3.14;

        c = a + b * 2;

        if (c > 20) {
            printf("c is greater than 20\\n");
        } else {
            printf("c is not greater than 20\\n");
        }

        int i = 1;
        int sum = 0;
        while (i <= 5) {
            sum = sum + i;
            i = i + 1;
        }
        printf("Sum from 1 to 5: %d\\n", sum);

        int result = add(a, b);
        printf("Result of add(%d, %d) = %d\\n", a, b, result);

        return 0;
    }

    int add(int x, int y) {
        return x + y;
    }
    """

    return compile_and_save(source_code, "test_simple")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_from_file(sys.argv[1])
    else:
        test_simple()