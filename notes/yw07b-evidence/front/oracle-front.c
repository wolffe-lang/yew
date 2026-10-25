/* Nonshipping adapter to pinned sagitta flcli.c:596-649, plus s29's
 * 500 KiB literal smoke. No oracle source or golden is modified. */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "fl/parse.h"
#include "util/intern.h"

extern int yew_fl_main(int argc, char **argv);
static unsigned long long nanos(void) {
    struct timespec t;
    (void)clock_gettime(CLOCK_MONOTONIC, &t);
    return (unsigned long long)t.tv_sec * 1000000000ULL + (unsigned long long)t.tv_nsec;
}
int main(int argc, char **argv) {
    if (argc == 3 && strcmp(argv[1], "ast") == 0) {
        argv[1] = "--dump-ast";
        return yew_fl_main(argc, argv);
    }
    if (argc == 2 && strcmp(argv[1], "perf") == 0) {
        char *src = malloc(512008U);
        size_t len = 1;
        unsigned long long start, elapsed;
        unsigned i;
        if (!src) return 3;
        src[0] = '[';
        while (len < 512000U - 2U) { memcpy(src + len, "123,", 4); len += 4; }
        src[len++] = ']';
        start = nanos();
        for (i = 0; i < 10; i++) {
            Arena arena;
            Interner in;
            DiagCtx dc;
            FlNode *root;
            arena_init(&arena);
            interner_init(&in, &arena);
            fl_diag_init(&dc, &arena);
            (void)fl_diag_add_file(&dc, "perf.fl", src, len);
            root = fl_parse_literal(&arena, &dc, &in, src, len, 0);
            if (!root || dc.nerrors) return 1;
            interner_free(&in);
            arena_free_all(&arena);
        }
        elapsed = nanos() - start;
        printf("front-perf: bytes=%zu rounds=10 elapsed_ns=%llu node_stride=%zu\n", len, elapsed, sizeof(FlNode));
        free(src);
        return 0;
    }
    return 2;
}
