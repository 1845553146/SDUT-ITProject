"""
编译器主程序
负责人：孔维正，将编译开始提示文字从英文改为中文，并添加个人标识
"""

import sys
import os
import argparse
import time

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


class Compiler:
    """编译器主类"""

    def __init__(self, source_code=None, filename=None):
        self.source_code = source_code
        self.filename = filename
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.tokens = []
        self.ast = None
        self.quads = []
        self.errors = []

        if filename and not source_code:
            self.load_file(filename)

    def load_file(self, filename):
        """从文件加载源代码"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
            self.filename = filename
            return True
        except Exception as e:
            self.errors.append(f"Failed to load file: {e}")
            return False

    def compile(self):
        """编译源代码"""
        if not self.source_code:
            self.errors.append("No source code provided")
            return False

        print("=" * 70)
        print(f"Compiling {'file: ' + self.filename if self.filename else 'source code'}")
        print("=" * 70)

        try:
            # 阶段1: 词法分析
            print("\n[阶段1] 词法分析")
            print("-" * 40)
            lexer = Lexer(self.source_code)
            self.tokens = lexer.tokenize()

            # 过滤EOF token显示
            display_tokens = [t for t in self.tokens if t.type != 'EOF']
            print(f"识别到 {len(display_tokens)} 个Token")

            if len(display_tokens) > 0:
                print("前20个Token:")
                for i, token in enumerate(display_tokens[:20]):
                    print(f"  [{i:2d}] {token.type:12s} '{token.value}'")
                if len(display_tokens) > 20:
                    print(f"  ... and {len(display_tokens) - 20} more tokens")

            # 阶段2: 语法分析
            print("\n[阶段2] 语法分析")
            print("-" * 40)
            lexer = Lexer(self.source_code)  # 重新初始化
            parser = Parser(lexer)
            self.ast = parser.parse()

            if self.ast:
                print("✓ 语法分析成功")
            else:
                print("✗ 语法分析失败")
                return False

            # 阶段3: 语义分析和中间代码生成
            print("\n[阶段3] 语义分析和中间代码生成")
            print("-" * 40)
            analyzer = SemanticAnalyzer()
            self.quads, sem_errors = analyzer.analyze(self.ast)
            self.errors.extend(sem_errors)

            if sem_errors:
                print(f"发现 {len(sem_errors)} 个语义错误")
            else:
                print("✓ 语义分析成功")

            # 输出中间代码
            print(f"\n生成的中间代码 ({len(self.quads)} 个四元式):")
            print("=" * 70)
            print("序号 | 操作符        | 操作数1   | 操作数2   | 结果")
            print("-" * 70)

            for i, quad in enumerate(self.quads):
                print(f"{i:3d} | {quad}")

            # 输出总结
            print("\n" + "=" * 70)
            print("编译结果:")
            if self.errors:
                print(f"✗ 编译完成，但有 {len(self.errors)} 个错误")
                for error in self.errors[:5]:  # 只显示前5个错误
                    print(f"  {error}")
                if len(self.errors) > 5:
                    print(f"  ... and {len(self.errors) - 5} more errors")
            else:
                print("✓ 编译成功完成!")
            print("=" * 70)

            return len(self.errors) == 0

        except Exception as e:
            print(f"\n✗ 编译过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_results(self, output_dir="output"):
        """保存编译结果"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_name = os.path.basename(self.filename) if self.filename else "source"
        base_name = os.path.splitext(base_name)[0]

        # 添加时间戳以避免覆盖
        timestamp = self.timestamp

        # 保存Token列表
        token_file = os.path.join(output_dir, f"{base_name}_{timestamp}_tokens.txt")
        with open(token_file, "w", encoding="utf-8") as f:
            f.write("Token列表:\n")
            f.write("=" * 60 + "\n")
            for i, token in enumerate(self.tokens):
                if token.type != 'EOF':
                    f.write(f"[{i:3d}] {token.type:12s} '{token.value}'\n")

        # 保存四元式
        quad_file = os.path.join(output_dir, f"{base_name}_{timestamp}_quads.txt")
        with open(quad_file, "w", encoding="utf-8") as f:
            f.write("四元式中间代码:\n")
            f.write("=" * 60 + "\n")
            f.write("序号 | 操作符        | 操作数1   | 操作数2   | 结果\n")
            f.write("-" * 60 + "\n")
            for i, quad in enumerate(self.quads):
                f.write(f"{i:3d} | {quad}\n")

        # 保存错误信息
        if self.errors:
            error_file = os.path.join(output_dir, f"{base_name}_{timestamp}_errors.txt")
            with open(error_file, "w", encoding="utf-8") as f:
                f.write("编译错误:\n")
                f.write("=" * 60 + "\n")
                for error in self.errors:
                    f.write(f"{error}\n")

        print(f"\n编译结果已保存到:")
        print(f"  Token列表: {token_file}")
        print(f"  四元式: {quad_file}")
        if self.errors:
            print(f"  错误信息: {error_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Simple C Subset Compiler")
    parser.add_argument("input_file", nargs="?", help="Input source file")
    parser.add_argument("-o", "--output", help="Output directory", default="output")
    parser.add_argument("-e", "--example", action="store_true", help="Run example")
    parser.add_argument("-n", "--no-overwrite", action="store_true", help="Don't overwrite existing files, add timestamp")

    args = parser.parse_args()

    if args.example:
        # 运行示例
        example_code = """
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
                printf("%d\\n", i);
            }

            return 0;
        }
        """

        compiler = Compiler(source_code=example_code)
        compiler.compile()
        compiler.save_results(args.output)

    elif args.input_file:
        # 编译文件
        compiler = Compiler(filename=args.input_file)
        success = compiler.compile()
        if success:
            compiler.save_results(args.output)
    else:
        # 交互模式
        print("Simple C Subset Compiler")
        print("Enter your source code (end with an empty line):")

        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break

        source_code = "\n".join(lines)

        if source_code.strip():
            compiler = Compiler(source_code=source_code)
            success = compiler.compile()
            if success:
                compiler.save_results(args.output)
        else:
            print("No source code provided")


if __name__ == "__main__":
    main()
