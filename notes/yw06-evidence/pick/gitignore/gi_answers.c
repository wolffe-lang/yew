/* C-only witness, not a port or a C fix: sagitta's tests/fuzz/
 * fuzz_gitignore.c at 9ace98c2, verbatim but for the ANSWER FOLD marked
 * "witness:" below.  C's driver prints no answers, so this twin folds
 * every answer its sessions ask of C's own matcher (gitignore.c) into one
 * FNV-1a hash, exactly as tools/fuzz-gitignore --answers folds the
 * port's; equal lines mean the port's matcher answered C's on every
 * (pattern, path) pair the campaign drew.  Linked as the Makefile links
 * fuzz_gitignore (Makefile:951-952, :1474-1476).
 */
#define _POSIX_C_SOURCE 200809L

/*
 * Sprint 26 §4 fuzz: the .gitignore compiler and matcher.
 *
 * WHAT IS BEING DEFENDED.  An ignore file is user-authored text that
 * reaches a pattern matcher, and the matcher runs against every path in
 * a 100 000-file walk.  Two failure modes matter and neither announces
 * itself:
 *
 *   THE BACKTRACKER LOOPS.  glob_match backtracks iteratively over `*`
 *   and `**`.  A pattern like `a**b**c` against a long path is exactly
 *   the shape that makes a naive backtracker take exponential time or
 *   never terminate — and a finder that hangs on one repository's
 *   .gitignore is indistinguishable from a crash, except nobody gets a
 *   core file.
 *
 *   IT READS PAST THE END.  Bracket sets scan forward for `]`, escapes
 *   consume the next byte, and `**` peeks at the one after.  Every one
 *   of those is an off-by-one waiting to happen on a truncated pattern,
 *   and ASan is how we find out.
 *
 * So: random pattern bytes, random path bytes, and a deliberate
 * adversarial set of shapes chosen to be hard rather than random.  The
 * check is not "does it match correctly" — that is test_gitignore.c's
 * job against known answers — it is "does it ANSWER at all, bounded,
 * without reading memory it does not own".
 */
#include "fuzzlib.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "util/arena.h"
#include "ws/gitignore.h"

/* witness: the answer fold. */
static u64 g_fold = UINT64_C(14695981039346656037);

static void fold(u64 v)
{
    g_fold = (g_fold ^ v) * UINT64_C(1099511628211);
}

typedef struct Rng {
    u64 s;
} Rng;

static u32 rng_next(Rng *r)
{
    r->s = r->s * 6364136223846793005ULL + 1442695040888963407ULL;
    return (u32)(r->s >> 33);
}

static u32 rng_below(Rng *r, u32 n)
{
    return n == 0U ? 0U : rng_next(r) % n;
}

static i64 now_ms(void)
{
    struct timespec ts;

    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        return 0;
    return (i64)ts.tv_sec * 1000 + (i64)ts.tv_nsec / 1000000;
}

/*
 * The bytes a real ignore file is made of, weighted toward the
 * metacharacters.  Uniform random bytes would spend almost all their
 * time on patterns that are one literal run and never reach the
 * backtracker at all.
 */
static const char gi_alphabet[] = "*?[]!^-/\\.abcXYZ09 \t#";

static void random_pattern(Rng *r, char *out, size_t cap)
{
    u32 len = rng_below(r, (u32)cap - 1U);
    u32 i;

    for (i = 0U; i < len; i++)
        out[i] = gi_alphabet[rng_below(r, (u32)sizeof(gi_alphabet) - 1U)];
    out[len] = '\0';
}

static void random_path(Rng *r, char *out, size_t cap)
{
    static const char path_alphabet[] = "abcXYZ09/._-";
    u32 len = 1U + rng_below(r, (u32)cap - 2U);
    u32 i;

    for (i = 0U; i < len; i++)
        out[i] =
            path_alphabet[rng_below(r, (u32)sizeof(path_alphabet) - 1U)];
    out[len] = '\0';
}

/*
 * Shapes chosen to be HARD, not random.
 *
 * Every one of these is a known way to make a glob matcher misbehave:
 * nested stars that each need backtracking, alternating star and
 * literal so no prefix ever settles, unterminated brackets, escapes at
 * the very end of the pattern where the next byte does not exist.
 */
static const char *const gi_adversarial[] = {
    "a**b**c**d**e",
    "*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*",
    "**/**/**/**/**",
    "[",
    "[]",
    "[!",
    "[a-",
    "[[[[[[[[",
    "]]]]]]]]",
    "\\",
    "a\\",
    "*\\",
    "[\\",
    "**",
    "/",
    "//",
    "///",
    "!",
    "!!",
    "!/",
    "*/",
    "/*",
    "a/**/b/**/c",
    "?????????????????????????",
    "*?*?*?*?*?*?*?*?*?*?",
    "[a-z][a-z][a-z][a-z][a-z][a-z][a-z][a-z]",
    "\\**\\**\\**",
    "#notacomment",
    "\\#escaped",
    "trailing   ",
    "trailing\\ ",
    "a[b-",
    "[^]",
    "[]]",
    "**a**"
};

/* One pattern against one path, bounded in time. */
static bool check_one(Arena *a, const char *pattern, const char *path,
                      char *why, size_t why_cap)
{
    GiSet *g;
    i64 start;
    i64 elapsed;
    char text[1200];

    (void)snprintf(text, sizeof(text), "%s\n", pattern);
    g = yew_gi_compile(a, NULL, text, (u64)strlen(text), NULL);
    /* A pattern that compiles to nothing is a legitimate answer — a
     * blank line, a comment, a lone `!`. */
    if (g == NULL) {
        fold(7U); /* witness */
        return true;
    }
    start = now_ms();
    {
        /* witness: the four answers, folded. */
        bool a = yew_gi_match(g, path, false);
        bool b = yew_gi_match(g, path, true);
        bool c = yew_gi_prunable(g, path);
        bool d = yew_gi_negated(g, path);

        fold((a ? 1U : 0U) + (b ? 2U : 0U) + (c ? 4U : 0U) + (d ? 8U : 0U));
    }
    elapsed = now_ms() - start;
    /*
     * 250 ms for four calls against one path is enormous — the real
     * numbers are nanoseconds.  Anything near this is a backtracker
     * that has gone exponential, which is the failure this bound
     * exists to catch before it becomes a hang in the field.
     */
    if (elapsed > 250) {
        (void)snprintf(why, why_cap,
                       "pattern '%s' took %lld ms against a %u-byte path",
                       pattern, (long long)elapsed,
                       (unsigned)strlen(path));
        return false;
    }
    return true;
}

static bool run_session(const u8 *data, size_t len, char *why,
                        size_t why_cap)
{
    Arena a;
    Rng rng;
    char pattern[128];
    char path[512];
    size_t k;
    u32 i;
    bool ok = true;

    rng.s = 0x9E3779B97F4A7C15ULL;
    for (k = 0U; k < len; k++)
        rng.s = rng.s * 31U + data[k];
    arena_init(&a);

    /* The case bytes themselves, as both pattern and path: random input
     * is its own test and reaches the tokenizer's error paths. */
    {
        size_t n = len < sizeof(pattern) - 1U ? len : sizeof(pattern) - 1U;

        (void)memcpy(pattern, data, n);
        pattern[n] = '\0';
        /* NULs and newlines would end the pattern early; they are worth
         * testing but not worth spending the whole budget on. */
        for (k = 0U; k < n; k++) {
            if (pattern[k] == '\0' || pattern[k] == '\n')
                pattern[k] = 'a';
        }
        random_path(&rng, path, sizeof(path));
        ok = check_one(&a, pattern, path, why, why_cap);
    }

    /* The adversarial shapes, each against a long path — a short path
     * cannot make a backtracker work hard. */
    for (i = 0U; ok && i < YEW_ARRAY_LEN(gi_adversarial); i++) {
        static const char long_path[] =
            "aaaaaaaaaa/bbbbbbbbbb/cccccccccc/dddddddddd/eeeeeeeeee/"
            "ffffffffff/gggggggggg/hhhhhhhhhh/iiiiiiiiii/jjjjjjjjjj/"
            "kkkkkkkkkk/llllllllll/mmmmmmmmmm/nnnnnnnnnn/oooooooooo.c";

        ok = check_one(&a, gi_adversarial[i], long_path, why, why_cap);
        if (ok) {
            random_path(&rng, path, sizeof(path));
            ok = check_one(&a, gi_adversarial[i], path, why, why_cap);
        }
    }

    /* And a round of purely random patterns from the weighted
     * alphabet. */
    for (i = 0U; ok && i < 64U; i++) {
        random_pattern(&rng, pattern, sizeof(pattern));
        random_path(&rng, path, sizeof(path));
        ok = check_one(&a, pattern, path, why, why_cap);
    }

    /*
     * A multi-rule file, since precedence and the negation scan walk
     * every rule: a set whose rules individually terminate could still
     * be pathological as a chain.
     */
    if (ok) {
        char text[4096];
        size_t at = 0U;
        GiSet *g;

        for (i = 0U; i < 32U && at + 130U < sizeof(text); i++) {
            random_pattern(&rng, pattern, sizeof(pattern));
            at += (size_t)snprintf(text + at, sizeof(text) - at, "%s\n",
                                   pattern);
        }
        g = yew_gi_compile(&a, NULL, text, (u64)at, NULL);
        if (g != NULL) {
            i64 start = now_ms();

            for (i = 0U; i < 32U; i++) {
                bool a;
                bool c;

                random_path(&rng, path, sizeof(path));
                a = yew_gi_match(g, path, (i & 1U) != 0U);
                c = yew_gi_prunable(g, path);
                fold((a ? 1U : 0U) + (c ? 4U : 0U)); /* witness */
            }
            if (now_ms() - start > 1000) {
                (void)snprintf(why, why_cap,
                               "a 32-rule set took %lld ms over 32 paths",
                               (long long)(now_ms() - start));
                ok = false;
            }
        } else {
            fold(7U); /* witness */
        }
    }

    arena_free_all(&a);
    return ok;
}

int main(int argc, char **argv)
{
    int status = yew_fuzz_main(argc, argv, "fuzz_gitignore", NULL, run_session);

    /* witness: the fold, after C's own report line. */
    if (status == 0)
        (void)printf("fuzz_gitignore: answers=%016llx\n",
                     (unsigned long long)g_fold);
    return status;
}
