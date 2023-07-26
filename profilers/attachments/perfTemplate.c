// #include "/full/path/to/test/file"
#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

typedef void (*traced_fun_t)();

long perf_event_open(struct perf_event_attr* hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags) {
    int ret;

    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

int set_up_perf_event(struct perf_event_attr* pe, unsigned long long config) {
    int fd;
    memset(pe, 0, sizeof(struct perf_event_attr));
    pe->type = PERF_TYPE_HARDWARE;
    pe->size = sizeof(struct perf_event_attr);
    pe->config = config;
    pe->disabled = 1;
    pe->exclude_kernel = 1;
    pe->exclude_hv = 1;

    fd = perf_event_open(pe, 0, -1, -1, 0);
    if (fd == -1) {
        fprintf(stderr, "Error opening leader %llx\n", pe->config);
        exit(EXIT_FAILURE);
    }
    return fd;
}

unsigned long long* traceFunction(traced_fun_t traced, unsigned long long* configs, int configs_len) {
    struct perf_event_attr pe[configs_len];
    unsigned long long* results = calloc(configs_len, sizeof(*results));
    int fd[configs_len];
    for (int i = 0; i < configs_len; i++) {
        fd[i] = set_up_perf_event(&pe[i], configs[i]);
    }

    for (int i = 0; i < configs_len; i++) {
        ioctl(fd[i], PERF_EVENT_IOC_RESET, 0);
    }

    for (int i = 0; i < configs_len; i++) {
        ioctl(fd[i], PERF_EVENT_IOC_ENABLE, 0);
    }

    traced();

    for (int i = 0; i < configs_len; i++) {
        ioctl(fd[i], PERF_EVENT_IOC_DISABLE, 0);
    }

    for (int i = 0; i < configs_len; i++) {
        read(fd[i], &results[i], sizeof(long long));
        close(fd[i]);
    }

    return results;
}

int main() {
    unsigned long long configs[] = {PERF_COUNT_HW_BRANCH_INSTRUCTIONS, PERF_COUNT_HW_BRANCH_MISSES,
                                    PERF_COUNT_HW_CACHE_BPU, PERF_COUNT_SW_CPU_CLOCK, PERF_COUNT_HW_INSTRUCTIONS};
    unsigned long long* data = traceFunction(test_fun, configs, sizeof(configs) / sizeof(*configs));
    printf("branches: %llu\n", data[0]);
    printf("missed_branches: %llu\n", data[1]);
    printf("cache_BPU: %llu\n", data[2]);
    printf("cpu_clock: %llu\n", data[3]);
    printf("instructions: %llu\n", data[4]);
}
