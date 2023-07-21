// #include "/full/path/to/test/file"
#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

typedef void (*traced_fun_t)();

typedef struct _perf_branch_data_t {
    unsigned long long branches;
    unsigned long long missed_branches;
    unsigned long long bpu;
} perf_branch_data_t;

long perf_event_open(struct perf_event_attr* hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags) {
    int ret;

    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

unsigned long long traceFunction(traced_fun_t traced, unsigned long long config) {
    struct perf_event_attr pe;
    long long count;
    int fd;

    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = config;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;

    fd = perf_event_open(&pe, 0, -1, -1, 0);
    if (fd == -1) {
        fprintf(stderr, "Error opening leader %llx\n", pe.config);
        exit(EXIT_FAILURE);
    }

    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    traced();

    ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
    read(fd, &count, sizeof(long long));
    close(fd);

    return count;
}

perf_branch_data_t fullTraceFunction(traced_fun_t traced) {
    perf_branch_data_t branch_data;
    branch_data.branches = traceFunction(traced, PERF_COUNT_HW_BRANCH_INSTRUCTIONS);
    branch_data.missed_branches = traceFunction(traced, PERF_COUNT_HW_BRANCH_MISSES);
    branch_data.bpu = traceFunction(traced, PERF_COUNT_HW_CACHE_BPU);
    return branch_data;
}

int main() {
    perf_branch_data_t res = fullTraceFunction(test_fun);
    printf("branches: %llu\n", res.branches);
    printf("missed_branches: %llu\n", res.missed_branches);
    printf("cache_BPU: %llu\n", res.bpu);
}
