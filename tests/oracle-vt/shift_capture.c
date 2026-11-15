/* Non-visual Shift-capture rows for the digest-pinned copied test VT.
 * This is test code only; neither the C editor nor any golden is changed. */
#include "vt.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void feed(VtScreen *v, const char *s)
{
    size_t i;
    /* Exercise escape sequences split at every byte. */
    for (i = 0u; s[i] != '\0'; i++)
        vt_feed(v, (const u8 *)s + i, 1u);
}

static int row(const char *name, bool ok)
{
    printf("%s %s\n", ok ? "PASS" : "FAIL", name);
    return ok ? 0 : 1;
}

static bool startup_restore(void)
{
    VtScreen v;
    VtCell before[8];
    u32 modes;
    bool ok;
    vt_init(&v, 2, 4);
    feed(&v, "\x1b[?1049hA\x1b[?2004h\x1b[?1002h\x1b[?1006h");
    memcpy(before, v.cells, sizeof(before));
    modes = v.modes;
    feed(&v, "\x1b[>1s");
    ok = v.nerrors == 0u && v.shift_capture && v.nshift_requests == 1u &&
         v.shift_request_modes == modes && v.nshift_early_requests == 0u &&
         v.modes == modes && v.cur_r == 0 && v.cur_c == 1 &&
         memcmp(before, v.cells, sizeof(before)) == 0;
    feed(&v, "\x1b[>0s");
    ok = ok && v.nerrors == 0u && !v.shift_capture && v.nshift_resets == 1u &&
         v.shift_reset_modes == modes && v.nshift_late_resets == 0u &&
         v.modes == modes && memcmp(before, v.cells, sizeof(before)) == 0;
    feed(&v, "\x1b[?2004l\x1b[?1002l\x1b[?1006l\x1b[>0s");
    ok = ok && v.nerrors == 0u && v.nshift_resets == 2u &&
         v.nshift_late_resets == 0u && !v.shift_capture;
    vt_free(&v);
    return ok;
}

static bool observes_bad_order(void)
{
    VtScreen v;
    bool ok;
    vt_init(&v, 2, 4);
    feed(&v, "\x1b[>1s\x1b[?1002h\x1b[?1006h\x1b[?1002l\x1b[?1006l\x1b[>0s");
    /* The protocol accepts these values; the order observer must flag them. */
    ok = v.nerrors == 0u && v.nshift_early_requests == 1u &&
         v.nshift_late_resets == 1u && !v.shift_capture;
    vt_free(&v);
    return ok;
}

static bool rejects_other_forms(void)
{
    static const char *const bad[] = {
        "\x1b[>2s", "\x1b[>3s", "\x1b[>999s", "\x1b[>s",
        "\x1b[>01s", "\x1b[>10s", "\x1b[>1;0s", "\x1b[>0;1s",
        "\x1b[>1:0s", "\x1b[>1 s", "\x1b[1s", "\x1b[>1S"
    };
    size_t i;
    bool ok = true;
    for (i = 0u; i < sizeof(bad) / sizeof(bad[0]); i++) {
        VtScreen v;
        vt_init(&v, 2, 4);
        feed(&v, bad[i]);
        if (v.nerrors == 0u || v.shift_capture || v.nshift_requests != 0u ||
            v.nshift_resets != 0u) {
            fprintf(stderr, "unexpected acceptance at rejection case %zu\n", i);
            ok = false;
        }
        vt_free(&v);
    }
    return ok;
}

static int captured_startup(const char *path)
{
    VtScreen v;
    unsigned char bytes[4096];
    size_t n;
    size_t total = 0u;
    FILE *f = fopen(path, "rb");
    bool ok;
    if (f == NULL) {
        perror("capture");
        return 2;
    }
    vt_init(&v, 24, 80);
    vt_set_restore_policy(&v, true);
    vt_set_primary_policy(&v, true);
    while ((n = fread(bytes, 1u, sizeof(bytes), f)) != 0u) {
        total += n;
        if (total > 16u * 1024u * 1024u) {
            fclose(f);
            vt_free(&v);
            fprintf(stderr, "capture exceeds 16 MiB\n");
            return 2;
        }
        vt_feed(&v, bytes, n);
    }
    ok = !ferror(f) && v.nerrors == 0u && v.nshift_requests > 0u &&
         v.nshift_resets > 0u && !v.shift_capture &&
         v.nshift_early_requests == 0u && v.nshift_late_resets == 0u;
    printf("capture errors=%u requests=%u resets=%u early=%u late=%u active=%d\n",
           (unsigned)v.nerrors, (unsigned)v.nshift_requests,
           (unsigned)v.nshift_resets, (unsigned)v.nshift_early_requests,
           (unsigned)v.nshift_late_resets, v.shift_capture ? 1 : 0);
    fclose(f);
    vt_free(&v);
    return row("startup-restore-capture", ok);
}

int main(int argc, char **argv)
{
    int failures;
    if (argc == 3 && strcmp(argv[1], "--capture") == 0)
        return captured_startup(argv[2]);
    if (argc != 1) {
        fprintf(stderr, "usage: shift-capture-test [--capture FILE]\n");
        return 2;
    }
    failures = row("startup-shift-capture-and-restore", startup_restore());
    failures += row("detect-shift-setup-order", observes_bad_order());
    failures += row("reject-other-shift-forms", rejects_other_forms());
    return failures == 0 ? 0 : 1;
}
