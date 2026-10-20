#include <stdio.h>
#include <string.h>
#include "search/regex.h"
#include "util/arena.h"
int main(void)
{
    static const char *pats[] = {
        "abcdefghijklmnopqrstuvwxyz0123456789ABCD",
        "abcdefghijklmnopqrstuvwxyz012345"
    };
    static const char hay[] = "--abcdefghijklmnopqrstuvwxyz012345XXXXXXXX--";
    for (int p = 0; p < 2; p++) {
        Arena a; YewReErr err = {0, NULL}; YewReMatch m;
        arena_init(&a);
        YewRe *re = yew_re_compile(&a, pats[p], strlen(pats[p]), YEW_RE_LITERAL, &err);
        YewReInput in = yew_re_input_bytes((const u8 *)hay, strlen(hay));
        bool got = yew_re_search(re, &in, BYTEOFF(0U), &m);
        printf("C: literal %zu bytes: got=%d span=%llu..%llu whole=%u\n", strlen(pats[p]), got,
               got ? (unsigned long long)m.g[0].lo : 0ULL, got ? (unsigned long long)m.g[0].hi : 0ULL,
               (unsigned)yew_re_whole_literal_bytes(re));
        arena_free_all(&a);
    }
    return 0;
}
