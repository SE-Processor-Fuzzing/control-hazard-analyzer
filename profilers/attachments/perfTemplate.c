#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

int* perf_fd;
size_t perf_fd_len;
unsigned long long configs[] = {PERF_COUNT_HW_BRANCH_INSTRUCTIONS, PERF_COUNT_HW_BRANCH_MISSES, PERF_COUNT_HW_CACHE_BPU,
                                PERF_COUNT_SW_CPU_CLOCK, PERF_COUNT_HW_INSTRUCTIONS};
char* value_names[] = {"branches", "missed_branches", "cache_BPU", "cpu_clock", "instructions"};

long perf_event_open(struct perf_event_attr* hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags) {
    int ret;

    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

int set_up_perf_event(unsigned long long config) {
    int fd;
    struct perf_event_attr* pe = malloc(sizeof(struct perf_event_attr));
    pe->type = PERF_TYPE_HARDWARE;
    pe->size = sizeof(struct perf_event_attr);
    pe->config = config;
    pe->disabled = 1;
    pe->exclude_kernel = 1;
    pe->exclude_hv = 1;

    fd = perf_event_open(pe, 0, -1, -1, 0);
    if (fd == -1) {
        fprintf(stderr, "Error opening leader %llx\n", pe->config);
        // exit(EXIT_FAILURE);
    }
    free(pe);
    return fd;
}

static void init() {
    size_t configs_len = sizeof(configs) / sizeof(*configs);
    perf_fd_len = configs_len;
    perf_fd = calloc(configs_len, sizeof(*perf_fd));
    for (int i = 0; i < configs_len; i++) {
        perf_fd[i] = set_up_perf_event(configs[i]);
    }

    for (int i = 0; i < configs_len; i++) {
        if (perf_fd[i] != -1)
            ioctl(perf_fd[i], PERF_EVENT_IOC_RESET, 0);
    }

    for (int i = 0; i < configs_len; i++) {
        if (perf_fd[i] != -1)
            ioctl(perf_fd[i], PERF_EVENT_IOC_ENABLE, 0);
    }
}

static void fin() {
    if (perf_fd != NULL) {
        for (int i = 0; i < perf_fd_len; i++) {
            if (perf_fd[i] != -1)
                ioctl(perf_fd[i], PERF_EVENT_IOC_DISABLE, 0);
        }

        long long value_result = -1;
        for (int i = 0; i < perf_fd_len; i++) {
            if (perf_fd[i] != -1) {
                read(perf_fd[i], &value_result, sizeof(long long));
                close(perf_fd[i]);
            } else {
                value_result = -1;
            }
            printf("%s: %lld\n", value_names[i], value_result);
        }
    }
    exit(0);
}

int main() {
    signal(SIGINT, fin);
    init();
    test_fun();
    fin();
}
