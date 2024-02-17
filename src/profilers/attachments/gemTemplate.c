#include <stdio.h>
#include <gem5/m5ops.h>

int main()
{
    m5_reset_stats(0, 0);

    test_fun();

    m5_exit(0);
}
