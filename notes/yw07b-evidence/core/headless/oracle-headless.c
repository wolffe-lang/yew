/* Reuse the PINNED harness's static programs, samples and measure function.
 * Only the entry point changes; no C source, baseline or golden is edited.
 * PERF_SOURCE is the exact oracle checkout's perf_fletch.c. */
#define main pinned_perf_fletch_main
#include PERF_SOURCE
#undef main

typedef struct Recorded { Sample sample; void *arg; u64 raw[WARMUP + REPS]; u32 n; } Recorded;
static u64 recorded_sample(void *ud) {
    Recorded *r = ud;
    u64 ns = r->sample(r->arg);
    r->raw[r->n++] = ns;
    return ns;
}
int main(int argc, char **argv) {
    Bench b = {0};
    ProgArg a = {0};
    Recorded r = {0};
    char *owned = NULL;
    unsigned i;
    if (argc < 2 || argc > 3) return 2;
    if (getenv("YEW_FL_GC_STRESS") || getenv("FL_GC_STRESS")) return 2;
    b.name = argv[1];
    a.name = argv[1];
    r.sample = sample_prog;
    r.arg = &a;
    if (!strcmp(argv[1], "startup")) { r.sample = sample_startup; b.budget = GATE_STARTUP_NS; }
    else if (!strcmp(argv[1], "parse_only")) {
        FILE *fp;
        long size;
        if (argc != 3 || !(fp = fopen(argv[2], "rb"))) return 2;
        if (fseek(fp, 0, SEEK_END) || (size = ftell(fp)) < 0 || fseek(fp, 0, SEEK_SET)) return 2;
        owned = malloc((size_t)size + 1U);
        if (!owned || fread(owned, 1, (size_t)size, fp) != (size_t)size) return 2;
        owned[size] = '\0';
        (void)fclose(fp);
        a.name = "runtime/init.fl"; a.src = owned; r.sample = sample_parse;
    }
    else if (!strcmp(argv[1], "motion_dispatch")) { a.src = SRC_MOTION; b.budget = (u64)GATE_MOTION_NS_PER_OP * MOTION_ITERS; }
    else if (!strcmp(argv[1], "fib27")) a.src = SRC_FIB27;
    else if (!strcmp(argv[1], "map_heavy")) a.src = SRC_MAP_HEAVY;
    else if (!strcmp(argv[1], "gc_pause")) { a.src = SRC_MAP_HEAVY; r.sample = sample_gc_pause; }
    else if (!strcmp(argv[1], "strbuild_join")) a.src = SRC_JOIN;
    else if (!strcmp(argv[1], "strbuild_concat")) a.src = SRC_CONCAT;
    else if (!strcmp(argv[1], "join5k")) a.src = SRC_JOIN_5K;
    else if (!strcmp(argv[1], "list_sort")) a.src = SRC_LIST_SORT;
    else return 2;
    measure(&b, recorded_sample, &r);
    printf("%s median_ns=%llu min_ns=%llu budget_ns=%llu raw=", b.name,
           (unsigned long long)b.median, (unsigned long long)b.min, (unsigned long long)b.budget);
    for (i = 0; i < r.n; ++i) printf("%s%llu", i ? "," : "", (unsigned long long)r.raw[i]);
    putchar('\n');
    free(owned);
    return 0;
}
