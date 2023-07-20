#include <stdio.h>
#include <gem5/m5ops.h>
#include <string>

int main()
{
    m5_reset_stats(0, 0);

    test_func();

    m5_exit(0);
}
