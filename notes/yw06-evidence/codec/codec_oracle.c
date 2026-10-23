/* Pure literal differential harness for sagitta 9ace98c2:
 * tests/unit/test_state_corpus.c:75-101, src/ws/state_fletch.c:193-244.
 * This links a COPY of pinned shipping objects, never the legacy codec. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "fl/data.h"
#include "fl/diag.h"
#include "fl/vm.h"
#include "util/arena.h"
#include "util/buf.h"
#include "util/intern.h"
#include "ws/state.h"

static int roundtrip(const Bytebuf *src, Bytebuf *out, int validate) {
    Arena a;
    Interner in;
    DiagCtx dc;
    FlVm vm;
    FlValue value;
    FlParseErr err;
    int ok;
    arena_init(&a);
    if (validate && yew_fl_parse_fletch(&a, src->data, src->len, &err) == NULL) {
        fprintf(stderr, "%u:%u: %s\n", err.line, err.col,
                err.msg == NULL ? "parse error" : err.msg);
        arena_free_all(&a);
        return 1;
    }
    interner_init(&in, &a);
    fl_diag_init(&dc, &a);
    (void)fl_vm_init(&vm, &a, &in, &dc);
    value = fl_data_read(&vm, (const char *)src->data, (size_t)src->len, &dc);
    ok = fl_diag_errors(&dc) == 0;
    if (ok) fl_data_write(out, value, 0U);
    fl_vm_free(&vm);
    interner_free(&in);
    arena_free_all(&a);
    return ok ? 0 : 1;
}
int main(int argc, char **argv) {
    Bytebuf src;
    unsigned char buf[65536];
    size_t n;
    FILE *f;
    int bench = argc == 4 && strcmp(argv[1], "--bench") == 0;
    const char *path = bench ? argv[2] : argc > 1 ? argv[1] : "";
    int rounds = bench ? atoi(argv[3]) : 1;
    unsigned long long sum = 0;
    if ((!bench && argc != 3) || rounds <= 0) return 2;
    f = fopen(path, "rb");
    if (f == NULL) return 2;
    bytebuf_init(&src);
    while ((n = fread(buf, 1, sizeof(buf), f)) != 0) bytebuf_append(&src, buf, n);
    if (ferror(f)) return 2;
    fclose(f);
    /* Perf compares ONE shipping pure-data read/write, not the corpus
     * helper's additional adapter parse. Differential mode checks both. */
    for (int i = 0; i < rounds; i++) {
        Bytebuf out;
        bytebuf_init(&out);
        if (roundtrip(&src, &out, !bench)) { bytebuf_free(&out); bytebuf_free(&src); return 1; }
        sum += out.len;
        if (!bench) {
            f = fopen(argv[2], "wb");
            if (f == NULL) return 2;
            if (fwrite(out.data, 1, out.len, f) != out.len || fclose(f)) return 2;
        }
        bytebuf_free(&out);
    }
    if (bench) printf("%llu\n", sum);
    bytebuf_free(&src);
    return 0;
}
