// 测试程序 - 符合简化语法规则
int main() {
    // 变量声明和初始化
    int a = 5, b = 10, c;
    float f = 3.14;

    // 赋值和算术运算
    c = a + b * 2;

    // 条件语句
    if (c > 20) {
        printf("c is greater than 20\n");
    } else {
        printf("c is not greater than 20\n");
    }

    // 循环语句
    int i = 1;
    int sum = 0;
    while (i <= 5) {
        sum = sum + i;
        i = i + 1;
    }
    printf("Sum from 1 to 5: %d\n", sum);

    // 函数调用
    int result = add(a, b);
    printf("Result of add(%d, %d) = %d\n", a, b, result);

    return 0;
}

// 另一个函数
int add(int x, int y) {
    return x + y;
}