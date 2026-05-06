// 循环语句测试
int main() {
    // while循环
    int i = 1;
    int sum = 0;
    while (i <= 10) {
        sum = sum + i;
        i = i + 1;
    }
    printf("Sum 1-10: %d\n", sum);

    // 计算阶乘
    int n = 5;
    int fact = 1;
    int j = 1;
    while (j <= n) {
        fact = fact * j;
        j = j + 1;
    }
    printf("Factorial of %d: %d\n", n, fact);

    return 0;
}