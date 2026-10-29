/*
 * cdump.c — yw13's C half of the porcelain differential: stdin (one
 * `git status --porcelain=v2 --branch -z` stream) through sagitta's own
 * yew_git_parse_status (src/mod/git/porcelain.c at 9ace98c2, linked from
 * the oracle build's porcelain.o and util/arena.o), printed in the
 * canonical line format `src/git_status_dump.lu` prints for the port's
 * parser. Paths are hex, so non-UTF-8 bytes compare exactly.
 *
 * Built and run by run.sh beside it; never part of the port's build.
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mod/git/git.h"
#include "util/arena.h"

/* The three util/base.c symbols arena.o needs, without the rest of it. */
void *yew_xmalloc(size_t size)
{
    void *p = malloc(size == 0U ? 1U : size);

    if (p == NULL)
        abort();
    return p;
}

void yew_xfree(void *p)
{
    free(p);
}

_Noreturn void yew_bug(const char *file, int line, const char *fmt, ...)
{
    va_list ap;

    (void)fprintf(stderr, "cdump: bug at %s:%d: ", file, line);
    va_start(ap, fmt);
    (void)vfprintf(stderr, fmt, ap);
    va_end(ap);
    (void)fputc('\n', stderr);
    abort();
}

static void hex(const char *p, size_t n)
{
    size_t i;

    if (p == NULL) {
        (void)fputs("-", stdout);
        return;
    }
    if (n == 0U) {
        (void)fputs("=", stdout);
        return;
    }
    for (i = 0U; i < n; i++)
        (void)printf("%02x", (unsigned)(unsigned char)p[i]);
}

static void str_hex(const char *s)
{
    hex(s, s == NULL ? 0U : strlen(s));
}

int main(void)
{
    static unsigned char buf[1U << 24];
    size_t n = fread(buf, 1U, sizeof(buf), stdin);
    GitSnapshot snap;
    GitParseErr err;
    bool ok;
    size_t i;

    (void)memset(&snap, 0, sizeof(snap));
    arena_init(&snap.a);
    (void)memset(&err, 0, sizeof(err));
    ok = yew_git_parse_status(&snap, buf, (u64)n, &err);
    (void)printf("ok %d\n", ok ? 1 : 0);
    if (!ok) {
        (void)printf("err %llu %s\n", (unsigned long long)err.off,
                     err.message);
        return 0;
    }
    (void)printf("state %d\n", (int)snap.state);
    (void)fputs("branch ", stdout);
    str_hex(snap.branch);
    (void)fputs("\nupstream ", stdout);
    str_hex(snap.upstream);
    (void)fputs("\nhead ", stdout);
    str_hex(snap.head_oid);
    (void)printf("\nab %d %d\n", (int)snap.ahead, (int)snap.behind);
    (void)printf("flags detached=%d unborn=%d conflicted=%d\n",
                 snap.detached ? 1 : 0, snap.unborn ? 1 : 0,
                 snap.conflicted ? 1 : 0);
    for (i = 0U; i < snap.entries.len; i++) {
        const GitEntry *e = &snap.entries.data[i];

        (void)printf("entry %d %c%c ", (int)e->kind, e->x, e->y);
        hex(e->path, e->path_len);
        (void)fputc(' ', stdout);
        if (e->orig_path == NULL)
            (void)fputs("-", stdout);
        else
            hex(e->orig_path, e->orig_len);
        (void)printf(" %u %s %d%d%d%d%d%d\n", (unsigned)e->score,
                     e->index_oid[0] == '\0' ? "-" : e->index_oid,
                     e->is_dir ? 1 : 0, e->submodule ? 1 : 0,
                     e->staged ? 1 : 0, e->unstaged ? 1 : 0,
                     e->untracked ? 1 : 0, e->conflicted ? 1 : 0);
    }
    for (i = 0U; i < snap.ignored.len; i++) {
        (void)fputs("ignored ", stdout);
        hex(snap.ignored.data[i].path, snap.ignored.data[i].len);
        (void)printf(" %d\n", snap.ignored.data[i].is_dir ? 1 : 0);
    }
    arena_free_all(&snap.a);
    return 0;
}
