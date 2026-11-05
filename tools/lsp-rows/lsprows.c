/*
 * yw11a: the LSP client's oracle rows. PTY sessions in which C yew (at
 * sagitta.pin) and the port each open the same `.lu` files against the
 * same language server, written over sagitta's own PTY harness at
 * 9ace98c2 (tests/pty/harness.c and the helpers of tests/pty/registry.c,
 * included whole as tools/trials/trials.c includes it). Never a golden:
 * the runner is this file's own main (tests/pty/runner.c's would hold
 * each case to a golden), each case runs twice, and every screen it
 * keeps (snapshot_write's format, the goldens' own) lands under
 * $YEW_LSPROW_OUT/run1 and run2; tools/run-lsp-rows holds the two runs
 * to each other and the C run's screens to the port's. Each case also
 * checks what it is about on the screen itself, so a binary without the
 * client fails by name.
 *
 * The real server: `wolf lsp` at yew's pin, found on the child's PATH
 * ($YEW_LSPROW_PATH) through C's compiled default row (client.c:89):
 *
 *   lspw_open_diag     a type error: the gutter sign, the underline and
 *                      the E:1 badge; ed.lsp.diag_next puts the cursor on
 *                      it and the hint on the statusline; ed.lsp.
 *                      diagnostics lists it
 *   lspw_edit_undo     an edit that breaks the file brings the error,
 *                      undo takes it away (the server's view follows)
 *   lspw_multicursor   one insert at two cursors breaks two lines (E:2);
 *                      undo mends both
 *
 * The error paths: tools/lsp-rows/fakeserver.py ($YEW_LSPROW_PYTHON,
 * $YEW_LSPROW_FAKE), configured as the `wolf` server by --config:
 *
 *   lspf_mirror_sync   incremental sync in UTF-16 over edits, a non-BMP
 *                      line, undo and two cursors; on save the server
 *                      compares its view with the file and says so
 *   lspf_crash         the server dies on save; at the editor's next
 *                      turn the client restarts it and the second
 *                      server's diagnostic arrives
 *   lspf_malformed     on save, a frame whose header is not a length: the
 *                      transport is dropped and the server restarted
 *   lspf_slow          initialize answered 1.5 s late: the editor takes
 *                      keys meanwhile, then syncs what was typed
 *   lspf_hang          initialize never answered: the deadline fires and
 *                      the editor quits without waiting on the server
 *   lspf_deaf_quit     shutdown and exit never answered: quitting is
 *                      bounded (client.c:1366-1410: 500 ms, then KILL)
 *
 * Build and run: tools/run-lsp-rows.
 */
#define yew_pty_cases yew_pty_cases_registry
#include "registry.c"
#undef yew_pty_cases

#include <sys/stat.h>
#include <ftw.h>

/* Which of a case's two runs is executing (1 or 2): its screens go to
 * $YEW_LSPROW_OUT/run<N>/. */
static unsigned lsprow_run = 1U;

/* Quiet after a semantic wait: the frame that follows the server's
 * message is complete and nothing else is pending. */
#define LSPROW_QUIET_MS 300

static void lsprow_dump(PtyCtx *c, const char *label)
{
    const char *out = getenv("YEW_LSPROW_OUT");
    char path[PATH_MAX];
    Bytebuf screen;
    int n;

    if (c->failed || out == NULL || out[0] == '\0')
        return;
    n = snprintf(path, sizeof(path), "%s/run%u/%s.%s.snap", out,
                 lsprow_run, c->test->name, label);
    if (n <= 0 || (size_t)n >= sizeof(path)) {
        ptc_check(c, false, "lsp row screen path overflow");
        return;
    }
    bytebuf_init(&screen);
    snapshot_write(&c->vt, &screen);
    if (!write_bytes(path, screen.data, screen.len))
        ptc_check(c, false, "could not keep the lsp row screen");
    bytebuf_free(&screen);
    if (getenv("YEW_LSPROW_RAW") != NULL) {
        n = snprintf(path, sizeof(path), "%s/run%u/%s.%s.raw", out,
                     lsprow_run, c->test->name, label);
        if (n > 0 && (size_t)n < sizeof(path))
            (void)write_bytes(path, c->raw.data, c->raw.len);
    }
}

static void lsprow_wait(PtyCtx *c, const char *text, const char *failure)
{
    s47_wait_screen(c, text, failure);
    ptc_settle(c, LSPROW_QUIET_MS);
}

static bool lsprow_screen_lacks(const PtyCtx *c, const void *arg)
{
    return !s43_screen_contains(&c->vt, (const char *)arg);
}

static void lsprow_wait_gone(PtyCtx *c, const char *text, const char *failure)
{
    ptc_wait_until(c, lsprow_screen_lacks, text, failure);
    ptc_settle(c, LSPROW_QUIET_MS);
}

static void lsprow_command(PtyCtx *c, const char *command)
{
    ptc_keys(c, ":");
    ptc_settle(c, 0);
    ptc_bytes(c, command);
    ptc_keys(c, "enter");
}

static bool lsprow_write(PtyCtx *c, const char *rel, const char *text)
{
    char path[PATH_MAX];
    int n = snprintf(path, sizeof(path), "%s/%s", c->workspace_dir, rel);

    if (n <= 0 || (size_t)n >= sizeof(path) ||
        !write_bytes(path, (const u8 *)text, strlen(text))) {
        ptc_check(c, false, "could not write an lsp row fixture");
        return false;
    }
    return true;
}

/* A wolf package in the case's workspace: wolf.pkg and src/main.lu. */
static bool lsprow_package(PtyCtx *c, const char *main_lu)
{
    char src[PATH_MAX];
    int n;

    if (c->workspace_dir == NULL) {
        ptc_check(c, false, "lsp row lacks a workspace");
        return false;
    }
    n = snprintf(src, sizeof(src), "%s/src", c->workspace_dir);
    if (n <= 0 || (size_t)n >= sizeof(src) ||
        (mkdir(src, 0700) != 0 && errno != EEXIST)) {
        ptc_check(c, false, "could not create the lsp row package");
        return false;
    }
    c->exec_path = getenv("YEW_LSPROW_PATH");
    return lsprow_write(c, "wolf.pkg",
                        "[package]\nname = \"rows\"\nversion = \"0.1.0\"\n") &&
           lsprow_write(c, "src/main.lu", main_lu);
}

/* Every row's config turns the shadow (ghost text, runtime/init.fl:37)
 * off: its LSP provider is yw11b's, and C's repaints for it once the
 * server is ready (ed.c:2690-2691). */
static const char lsprow_shadow_off[] = "set({\"shadow.enable\": false})\n";

static bool lsprow_config(PtyCtx *c, const char *extra, char *config,
                          size_t cap)
{
    char source[PATH_MAX * 4U];
    int n = snprintf(config, cap, "%s/rows.fl", c->state_dir);
    int m = snprintf(source, sizeof(source), "%s%s", lsprow_shadow_off,
                     extra);

    if (n <= 0 || (size_t)n >= cap || m <= 0 || (size_t)m >= sizeof(source) ||
        !write_bytes(config, (const u8 *)source, (size_t)m)) {
        ptc_check(c, false, "could not write the lsp row config");
        return false;
    }
    return true;
}

/* No `lsp` binding: the table is C's compiled default (client.c:76-98),
 * `wolf lsp` for the `wolf` language. */
static void lsprow_open(PtyCtx *c)
{
    char config[PATH_MAX];

    if (!lsprow_config(c, "", config, sizeof(config)))
        return;
    ptc_spawn(c, ptc_yew_bin(c), "--config", config, "src/main.lu", NULL);
    ptc_wait_kitty_push(c, 21U);
}

/* The fake server as the `wolf` row of init.fl's table, opened. */
static void lsprow_open_fake(PtyCtx *c, const char *mode, int timeout_ms)
{
    const char *python = getenv("YEW_LSPROW_PYTHON");
    const char *fake = getenv("YEW_LSPROW_FAKE");
    char config[PATH_MAX];
    char source[PATH_MAX * 4U];
    int n;

    if (python == NULL || fake == NULL) {
        ptc_check(c, false, "YEW_LSPROW_PYTHON and YEW_LSPROW_FAKE unset");
        return;
    }
    n = snprintf(source, sizeof(source),
                 "let lsp = {servers: {wolf: {id: \"fake\", cmd: \"%s\", "
                 "args: [\"%s\", \"%s\", \"%s/fake.marker\"], "
                 "roots: [\"wolf.pkg\"], init_options: nil, "
                 "init_timeout_ms: %d}}}\n",
                 python, fake, mode, c->state_dir, timeout_ms);
    if (n <= 0 || (size_t)n >= sizeof(source)) {
        ptc_check(c, false, "lsp row config overflow");
        return;
    }
    if (!lsprow_config(c, source, config, sizeof(config)))
        return;
    ptc_spawn(c, ptc_yew_bin(c), "--config", config, "src/main.lu", NULL);
    ptc_wait_kitty_push(c, 21U);
}

static const char lsprow_typed_error[] =
    "fn main() -> int {\n"
    "    let x: int = \"three\"\n"
    "    x\n"
    "}\n";

static const char lsprow_clean[] =
    "fn main() -> int {\n"
    "    let x: int = 3\n"
    "    x\n"
    "}\n";

static const char lsprow_two_lets[] =
    "fn main() -> int {\n"
    "    let a: int = 1\n"
    "    let b: int = 2\n"
    "    a + b\n"
    "}\n";

static void case_lspw_open_diag(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_typed_error))
        return;
    lsprow_open(c);
    lsprow_wait(c, "E:1", "wolf lsp's diagnostic never reached the badge");
    lsprow_dump(c, "1-open");
    lsprow_command(c, "ed.lsp.diag_next");
    /* The hint is the message's first line (message.c:108-138). */
    lsprow_wait(c, "this is `str`", "diag_next did not show the hint");
    /* Screen row 0 is the tab strip. */
    ptc_check(c, c->vt.cur_r == 2U, "diag_next did not reach line 2");
    lsprow_dump(c, "2-next");
    lsprow_command(c, "ed.lsp.diagnostics");
    ptc_settle(c, 500);
    lsprow_dump(c, "3-list");
    /* The picker's footer: the alias hint for the long command name
     * covers its title row in both editors. */
    ptc_check(c, s43_screen_contains(&c->vt, "tab scope"),
              "the diagnostic list did not open");
    ptc_keys(c, "esc");
    ptc_settle(c, LSPROW_QUIET_MS);
    force_quit(c);
}

static void case_lspw_edit_undo(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open(c);
    lsprow_wait(c, "wolf", "the wolf server never showed on the statusline");
    lsprow_dump(c, "1-open");
    ptc_keys(c, "down down end i y esc");
    lsprow_wait(c, "E:1", "the edit's error never came back from wolf lsp");
    lsprow_dump(c, "2-edit");
    ptc_keys(c, "u");
    lsprow_wait_gone(c, "E:1", "undo did not clear wolf lsp's error");
    lsprow_dump(c, "3-undo");
    force_quit(c);
}

static void case_lspw_multicursor(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_two_lets))
        return;
    lsprow_open(c);
    lsprow_wait(c, "wolf", "the wolf server never showed on the statusline");
    ptc_keys(c, "down");
    ptc_settle(c, 0);
    lsprow_command(c, "ed.cursor.add.below");
    ptc_settle(c, LSPROW_QUIET_MS);
    ptc_keys(c, "i z esc");
    lsprow_wait(c, "E:2", "two cursors' insert did not bring two errors");
    lsprow_dump(c, "1-two");
    ptc_keys(c, "u");
    lsprow_wait_gone(c, "E:2", "undo did not mend both lines");
    lsprow_dump(c, "2-undo");
    force_quit(c);
}

static const char lsprow_mirror_text[] =
    "fn main() -> int {\n"
    "    // \xf0\x9d\x84\x9e clef\n"
    "    let a: int = 1\n"
    "    let b: int = 2\n"
    "    a + b\n"
    "}\n";

static void case_lspf_mirror_sync(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_mirror_text))
        return;
    lsprow_open_fake(c, "mirror", 30000);
    lsprow_wait(c, "fake", "the fake server never showed on the statusline");
    /* After the clef (a surrogate pair in UTF-16), an insert. */
    ptc_keys(c, "down end i ! esc");
    ptc_settle(c, LSPROW_QUIET_MS);
    /* A deletion across a line join. */
    ptc_keys(c, "down end i delete esc");
    ptc_settle(c, LSPROW_QUIET_MS);
    /* Two cursors. */
    lsprow_command(c, "ed.cursor.add.below");
    ptc_settle(c, LSPROW_QUIET_MS);
    ptc_keys(c, "i q esc");
    ptc_settle(c, LSPROW_QUIET_MS);
    ptc_keys(c, "u");
    ptc_settle(c, LSPROW_QUIET_MS);
    lsprow_command(c, "ed.cursor.collapse");
    ptc_settle(c, LSPROW_QUIET_MS);
    ptc_keys(c, "i w esc s g g");
    lsprow_wait(c, "view ", "the fake server never answered the save");
    ptc_check(c, s43_screen_contains(&c->vt, "view matches disk"),
              "the server's view differs from the saved buffer");
    lsprow_dump(c, "1-saved");
    force_quit(c);
}

/* Save (the fake's trigger), let the restart's 250 ms delay pass
 * (client.c:768), then one key: C's loop wakes for a running job's
 * deadline only (job.c:1879-1915), so a dead server is restarted at the
 * editor's next turn. */
static void lsprow_after_trigger(PtyCtx *c)
{
    ptc_keys(c, "s");
    ptc_settle(c, 600);
    ptc_keys(c, "esc");
    lsprow_wait(c, "after the restart",
                "the restarted server's diagnostic never arrived");
}

static void case_lspf_crash(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open_fake(c, "crash", 30000);
    lsprow_wait(c, "before the crash",
                "the first server's diagnostic never arrived");
    lsprow_dump(c, "1-before");
    lsprow_after_trigger(c);
    lsprow_dump(c, "2-after");
    force_quit(c);
}

static void case_lspf_malformed(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open_fake(c, "malformed", 30000);
    lsprow_wait(c, "before the crash",
                "the first server's diagnostic never arrived");
    lsprow_dump(c, "1-before");
    lsprow_after_trigger(c);
    lsprow_dump(c, "2-after");
    force_quit(c);
}

static void case_lspf_slow(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open_fake(c, "slow", 30000);
    ptc_keys(c, "i a b c esc");
    s47_wait_screen(c, "abcfn main", "the editor did not take keys while "
                                      "initialize was pending");
    lsprow_dump(c, "1-pending");
    /* Past the 1.5 s reply. The badge keeps its ellipsis until the next
     * repaint (registry.c:9886-9888 says as much of C), so the save is
     * what the row waits on. */
    ptc_settle(c, 2000);
    ptc_keys(c, "s g g");
    lsprow_wait(c, "view ", "the late server never answered the save");
    ptc_check(c, s43_screen_contains(&c->vt, "view matches disk"),
              "the late server's view differs from the saved buffer");
    lsprow_dump(c, "2-saved");
    force_quit(c);
}

static void case_lspf_hang(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open_fake(c, "hang", 1000);
    ptc_settle(c, 2000);
    /* Past the deadline: the server is still the buffer's (its badge),
     * no longer initializing (no ellipsis) and no longer a job (no
     * <1> badge): killed, and nothing said (client.c:833-844). */
    ptc_check(c, s43_screen_contains(&c->vt, "fake") &&
                     !s43_screen_contains(&c->vt, "fake\xe2\x80\xa6") &&
                     !s43_screen_contains(&c->vt, "\xe2\x9f\xa8" "1\xe2\x9f\xa9"),
              "the initialize deadline did not end the server");
    lsprow_dump(c, "1-deadline");
    force_quit(c);
}

static void case_lspf_deaf_quit(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_clean))
        return;
    lsprow_open_fake(c, "deaf", 30000);
    lsprow_wait(c, "fake", "the fake server never showed on the statusline");
    ptc_settle(c, 500);
    ptc_keys(c, "s");
    lsprow_wait(c, "view matches disk", "the deaf server never answered the save");
    lsprow_dump(c, "1-ready");
    force_quit(c);
}

/* registry.c #undefs its C() macro at its end, so the rows are spelled
 * out: {name, profile, rows, cols, fn, xfail_id}. */
static const PtyCase lsprow_cases[] = {
    {"lspw_open_diag", "modern", 24U, 80U, case_lspw_open_diag, NULL},
    {"lspw_edit_undo", "modern", 24U, 80U, case_lspw_edit_undo, NULL},
    {"lspw_multicursor", "modern", 24U, 80U, case_lspw_multicursor, NULL},
    {"lspf_mirror_sync", "modern", 24U, 80U, case_lspf_mirror_sync, NULL},
    {"lspf_crash", "modern", 24U, 80U, case_lspf_crash, NULL},
    {"lspf_malformed", "modern", 24U, 80U, case_lspf_malformed, NULL},
    {"lspf_slow", "modern", 24U, 80U, case_lspf_slow, NULL},
    {"lspf_hang", "modern", 24U, 80U, case_lspf_hang, NULL},
    {"lspf_deaf_quit", "modern", 24U, 80U, case_lspf_deaf_quit, NULL},
    {NULL, NULL, 0U, 0U, NULL, NULL}
};

static int lsprow_rm(const char *path, const struct stat *st, int flag,
                     struct FTW *ftw)
{
    (void)st;
    (void)flag;
    (void)ftw;
    return remove(path);
}

/* One run of one case in a fresh state directory (the harness makes it
 * absolute and puts the workspace inside), removed when the run passes.
 * The pty runner's hermetic user init.fl (runner.c:204) is not written:
 * the wolf cases want the compiled table, the fake cases pass --config. */
static bool lsprow_once(const PtyCase *test, const char *demo,
                        const char *yew, i64 case_budget, i64 deadline)
{
    char state[PATH_MAX];
    char *base = realpath("build", NULL);
    PtyCtx ctx;
    bool ok;
    int n;

    /* A fixed name under the real directory `build` links to: the
     * diagnostic list labels a row by the buffer's whole path (diag.c:
     * 638-643, yew_buf_label at ed.c:333-340), so C's run and the port's
     * must open the same path, and no mkdtemp suffix may reach a screen. */
    n = base == NULL ? -1 :
        snprintf(state, sizeof(state), "%s/lsprow-%s-%u", base, test->name,
                 lsprow_run);
    free(base);
    if (n > 0 && (size_t)n < sizeof(state))
        (void)nftw(state, lsprow_rm, 16, FTW_DEPTH | FTW_PHYS);
    if (n <= 0 || (size_t)n >= sizeof(state) || mkdir(state, 0700) != 0) {
        (void)fprintf(stderr, "lsp-row: %s: cannot create state dir\n",
                      test->name);
        return false;
    }
    (void)memset(&ctx, 0, sizeof(ctx));
    ptc_init(&ctx, test, state, demo, yew, case_budget, deadline);
    test->fn(&ctx);
    ptc_cleanup(&ctx);
    ok = !ctx.failed;
    if (ok)
        (void)nftw(state, lsprow_rm, 16, FTW_DEPTH | FTW_PHYS);
    else
        (void)fprintf(stderr, "lsp-row: %s run %u: %s (state kept: %s)\n",
                      test->name, lsprow_run,
                      ctx.failure[0] == '\0' ? "failed" : ctx.failure,
                      state);
    ptc_dispose(&ctx);
    return ok;
}

int main(int argc, char **argv)
{
    const char *demo = NULL;
    const char *yew = NULL;
    const char *filter = getenv("YEW_PTY_FILTER");
    const char *budget_text = getenv("YEW_PTY_CASE_BUDGET_MS");
    i64 case_budget = budget_text != NULL ? atoll(budget_text) : 60000;
    i64 deadline;
    bool ok = true;
    size_t i;
    int a;

    for (a = 1; a + 1 < argc; a += 2) {
        if (strcmp(argv[a], "--demo") == 0)
            demo = argv[a + 1];
        else if (strcmp(argv[a], "--yew") == 0)
            yew = argv[a + 1];
    }
    if (demo == NULL || yew == NULL || a != argc) {
        (void)fprintf(stderr, "usage: lsprows_runner --demo DEMO --yew YEW\n");
        return 2;
    }
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR)
        return 1;
    deadline = ptc_now_ms() + 1350000;
    for (i = 0U; lsprow_cases[i].name != NULL; i++) {
        const PtyCase *test = &lsprow_cases[i];
        bool both = true;

        if (filter != NULL && filter[0] != '\0' &&
            strstr(test->name, filter) == NULL)
            continue;
        for (lsprow_run = 1U; lsprow_run <= 2U && both; lsprow_run++)
            both = lsprow_once(test, demo, yew, case_budget, deadline);
        if (!ptc_sweep_all()) {
            (void)fprintf(stderr, "lsp-row: %s: live children outlived the case\n",
                          test->name);
            both = false;
        }
        if (both)
            (void)printf("lsp-row: %s: ok\n", test->name);
        else
            (void)printf("FAIL %s\n", test->name);
        (void)fflush(stdout);
        ok = ok && both;
    }
    return ok ? 0 : 1;
}
