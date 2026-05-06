// 条件语句测试
int main() {
    int x = 15, y = 20;

    if (x > y) {
        printf("x is greater than y\n");
    } else if (x < y) {
        printf("x is less than y\n");
    } else {
        printf("x is equal to y\n");
    }

    // 嵌套if
    int age = 25;
    if (age >= 18) {
        if (age >= 60) {
            printf("Senior\n");
        } else {
            printf("Adult\n");
        }
    } else {
        printf("Minor\n");
    }

    return 0;
}