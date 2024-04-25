#define _GNU_SOURCE
#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

void test_fun();

#define EXIT_SIGNAL 2

#ifndef EVENTS_INIT
    #define EVENTS_INIT

    #define EVENTS_EXCLUDE_KERNEL 1
    #define EVENTS_EXCLUDE_HV     1
typedef struct _perf_event_config_t {
    unsigned int type;
    unsigned long long config;
    char* name;
} perf_event_config_t;

perf_event_config_t events[] = {};
size_t events_len = 0;

#endif

typedef struct _perf_group_t {
    int group_fd;
    int* perf_fd;
    size_t perf_fd_len;
} perf_group_t;

perf_group_t* perf_group = NULL;

long perf_event_open(struct perf_event_attr* hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags) {
    int ret;
    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
    return ret;
}

int set_up_perf_event(perf_event_config_t* event, int cpu, int group_fd) {
    int fd;
    struct perf_event_attr* pe = malloc(sizeof(struct perf_event_attr));
    pe->type = event->type;
    pe->size = sizeof(struct perf_event_attr);
    pe->config = event->config;
    pe->disabled = 1;
    pe->exclude_kernel = EVENTS_EXCLUDE_KERNEL;
    pe->exclude_hv = EVENTS_EXCLUDE_HV;

    fd = perf_event_open(pe, 0, cpu, group_fd, 0);
    if (fd == -1) {
        fprintf(stderr, "Error opening leader %llx\n", pe->config);
    }
    free(pe);
    return fd;
}

perf_group_t* create_perf_group(perf_event_config_t* events, size_t len, int cpu) {
    perf_group_t* group = calloc(1, sizeof(*group));
    group->perf_fd_len = len;
    group->perf_fd = calloc(events_len, sizeof(*(group->perf_fd)));

    int group_fd = -1;
    for (size_t i = 0; i < events_len; i++) {
        group->perf_fd[i] = set_up_perf_event(&events[i], cpu, group_fd);
        if (group->perf_fd[i] > -1)
            group_fd = group->perf_fd[i];
    }

    if (group_fd < 0) {
        fprintf(stderr, "Can't set up any perf event\n");
        exit(EXIT_FAILURE);
    }

    group->group_fd = group_fd;
    return group;
}

void delete_perf_group_t(perf_group_t* group) {
    if (group != NULL) {
        for (size_t i = 0; i < perf_group->perf_fd_len; i++) {
            if (group->perf_fd[i] > -1)
                close(group->perf_fd[i]);
        }

        free(group->perf_fd);
        free(group);
    }
}

void group_reset_counters(perf_group_t* group) { ioctl(group->group_fd, PERF_EVENT_IOC_RESET, 0); }
void group_enable_counters(perf_group_t* group) { ioctl(group->group_fd, PERF_EVENT_IOC_ENABLE, 0); }
void group_disable_counters(perf_group_t* group) { ioctl(group->group_fd, PERF_EVENT_IOC_DISABLE, 0); }
long long group_get_counter(perf_group_t* group, size_t index) {
    long long value_result = -1;

    if (group->perf_fd[index] > -1) {
        read(group->perf_fd[index], &value_result, sizeof(long long));
    }
    return value_result;
}

static void init(int cpu) {
    perf_group = create_perf_group(events, events_len, cpu);
    group_reset_counters(perf_group);
    group_enable_counters(perf_group);
}

static void fin() {
    signal(SIGINT, SIG_IGN);
    if (perf_group != NULL) {
        group_disable_counters(perf_group);

        long long value_result = -1;
        for (size_t i = 0; i < perf_group->perf_fd_len; i++) {
            value_result = group_get_counter(perf_group, i);
            if (value_result < 0) {
                fprintf(stderr, "Can't read value of '%s'\n", events[i].name);
                value_result = -1;
            }
            printf("%s: %lld\n", events[i].name, value_result);
        }
        delete_perf_group_t(perf_group);
    }
}

static void sigint_handler() { exit(EXIT_SIGNAL); }

int main(int argc, char* argv[]) {
    atexit(fin);
    signal(SIGINT, sigint_handler);

    struct sched_param sp;
    sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
    sched_setscheduler(0, SCHED_FIFO, &sp);

    cpu_set_t cpuset;
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <cpu>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    int cpu = atoi(argv[1]);
    CPU_ZERO(&cpuset);
    CPU_SET(cpu, &cpuset);
    if (sched_setaffinity(0, sizeof(cpuset), &cpuset) == -1) {
        fprintf(stderr, "Can't set test to %d CPU core\n", cpu);
    }

    init(cpu);
    test_fun();
    return 0;
}
