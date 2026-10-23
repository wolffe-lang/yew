/*
 * yw06 (R-yw06-3 = A): M-YW5's automated twins of the field boxes the
 * port can answer today — "Workspace resume in anger" (s42 §10 :495,
 * >= 20 cycles) and the restore trials of "Zero data loss" / "Terminal
 * restore in the field" (:469, :476) — written over sagitta's own PTY
 * harness at 9ace98c2 (tests/pty/harness.c, the s25 helpers of
 * tests/pty/registry.c:6230-6400), lane evidence, never a golden.
 *
 * registry.c is included whole so its static s25 helpers are in scope;
 * its case table is renamed out of the way and this file's four cases
 * are the runner's table. Each case builds s25_resume_exact's arrangement
 * (six files, three grouped, two panes, a CJK cursor, a scrolled view, two
 * jumplist entries) and ends on the C golden `s25_resume_exact`, so the
 * last grid is held to C's as well as to the first process's:
 *
 *   trial_resume_cycles20   quit and reopen twenty times; every reopened
 *                           grid byte-identical to the one before the
 *                           first quit (ptc_check_resume_exact)
 *   trial_restore_sigkill   the debounced save (2,000 ms, state.h:76)
 *   trial_restore_sigsegv   allowed to land, then the editor killed by the
 *   trial_restore_hangup    signal / its terminal closed (SIGHUP, the
 *                           kernel's signal to the controlling process);
 *                           the reopened grid is the arrangement exactly —
 *                           a fatal path saves nothing (s25 §5), so what
 *                           comes back is the last save, whole
 *
 *   trial_cross_differential  the arrangement built and saved by THIS
 *                           binary (the runner's --yew) and resumed by the
 *                           OTHER (YEW_TRIAL_OTHER: C for the port, the
 *                           port for C) — the other's grid the first's,
 *                           exactly, and the two saved state.fl documents
 *                           byte-identical but for `saved_at` (s25's
 *                           C<->port differential, both ways)
 *
 * Signals go only to the editor this runner spawned, inside the lane's
 * container (RULES §5). Build and run: run-trials.sh.
 */
#define yew_pty_cases yew_pty_cases_registry
#include "registry.c"
#undef yew_pty_cases

/* The debounce's 2,000 ms plus margin, measured as output quiet. */
#define TRIAL_DEBOUNCE_QUIET_MS 2600

static void case_trial_resume_cycles20(PtyCtx *c)
{
    int cycle;

    s25_fixture_make();
    s25_spawn_bare(c);
    s25_build_session(c);
    if (c->failed) {
        s25_fixture_remove();
        return;
    }
    ptc_mark_resume(c);
    for (cycle = 0; cycle < 20 && !c->failed; cycle++) {
        /* The harness resumes once a case (harness.c:1886-1889); a cycle
         * is that resume again against the SAME first grid. */
        c->resumed = false;
        force_quit(c);
        s25_resume_bare(c);
        ptc_check_resume_exact(c);
        if (c->failed)
            (void)fprintf(stderr, "trial: cycle %d diverged\n", cycle + 1);
    }
    if (!c->failed)
        (void)fprintf(stderr, "trial: 20 cycles grid-identical\n");
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    s25_fixture_remove();
}

static void trial_kill(PtyCtx *c, int how)
{
    s25_fixture_make();
    /* Before the spawn, or the harness ignores it (harness.c:1488-1494):
     * a death leaves the alternate screen, and the port's guard sibling
     * (#93 R1 B) also restores after a SIGKILL, which C cannot, writing
     * tty.c:157's note to the primary screen. */
    ptc_allow_primary(c);
    ptc_allow_restore(c);
    s25_spawn_bare(c);
    s25_build_session(c);
    if (c->failed) {
        s25_fixture_remove();
        return;
    }
    ptc_settle(c, TRIAL_DEBOUNCE_QUIET_MS);
    ptc_mark_resume(c);
    /* SIGHUP is the terminal closing: the signal the kernel sends the
     * session's controlling process when the master end goes away (the
     * harness keeps its master open, so it is sent by hand). */
    if (kill(c->pty.pid, how) != 0) {
        ptc_check(c, false, "could not signal the live editor");
        s25_fixture_remove();
        return;
    }
    s25_resume_bare(c);
    ptc_check_resume_exact(c);
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    s25_fixture_remove();
}

static void case_trial_restore_sigkill(PtyCtx *c)
{
    trial_kill(c, SIGKILL);
}

static void case_trial_restore_sigsegv(PtyCtx *c)
{
    trial_kill(c, SIGSEGV);
}

static void case_trial_restore_hangup(PtyCtx *c)
{
    trial_kill(c, SIGHUP);
}

/* The one state.fl under XDG_STATE_HOME (the case's state dir). */
static bool trial_state_read(PtyCtx *c, Bytebuf *out)
{
    char dir[PATH_MAX];
    char path[PATH_MAX + 64];
    DIR *d;
    struct dirent *e;
    FILE *f;
    u8 chunk[4096];
    size_t got;
    bool found = false;

    out->len = 0U;
    (void)snprintf(dir, sizeof(dir), "%s/yew/workspaces", c->state_dir);
    d = opendir(dir);
    if (d == NULL)
        return false;
    while ((e = readdir(d)) != NULL) {
        if (e->d_name[0] == '.')
            continue;
        (void)snprintf(path, sizeof(path), "%s/%s/state.fl", dir, e->d_name);
        found = true;
        break;
    }
    (void)closedir(d);
    if (!found)
        return false;
    f = fopen(path, "rb");
    if (f == NULL)
        return false;
    while ((got = fread(chunk, 1U, sizeof(chunk), f)) > 0U)
        bytebuf_append(out, chunk, got);
    (void)fclose(f);
    return out->len != 0U;
}

/* `saved_at` is the one field a save stamps (compare_live.py's rule). */
static void trial_normalize(Bytebuf *b)
{
    Bytebuf o;
    size_t i = 0U;

    bytebuf_init(&o);
    while (i < b->len) {
        size_t e = i;

        while (e < b->len && b->data[e] != '\n')
            e++;
        if (e < b->len)
            e++;
        if (!(e - i > 13U && memcmp(b->data + i, "    saved_at:", 13U) == 0))
            bytebuf_append(&o, b->data + i, e - i);
        i = e;
    }
    b->len = 0U;
    bytebuf_append(b, o.data, o.len);
    bytebuf_free(&o);
}

static void case_trial_cross_differential(PtyCtx *c)
{
    const char *other = getenv("YEW_TRIAL_OTHER");
    Bytebuf first;
    Bytebuf second;

    if (other == NULL || other[0] == '\0') {
        ptc_check(c, false, "YEW_TRIAL_OTHER names no second editor");
        return;
    }
    bytebuf_init(&first);
    bytebuf_init(&second);
    s25_fixture_make();
    s25_spawn_bare(c);
    s25_build_session(c);
    if (c->failed)
        goto done;
    ptc_mark_resume(c);
    force_quit(c);
    ptc_cleanup(c);
    if (!trial_state_read(c, &first)) {
        ptc_check(c, false, "the first editor left no state.fl");
        goto done;
    }
    ptc_resume(c, other, NULL);
    ptc_settle(c, 0);
    ptc_wait_kitty_push(c, 21U);
    ptc_check_resume_exact(c);
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    ptc_cleanup(c);
    if (!trial_state_read(c, &second)) {
        ptc_check(c, false, "the second editor left no state.fl");
        goto done;
    }
    trial_normalize(&first);
    trial_normalize(&second);
    if (first.len != second.len ||
        memcmp(first.data, second.data, first.len) != 0) {
        ptc_check(c, false, "the two editors' state.fl differ beyond saved_at");
        (void)fwrite(first.data, 1U, first.len, stderr);
        (void)fwrite(second.data, 1U, second.len, stderr);
    } else {
        (void)fprintf(stderr, "trial: state.fl byte-identical but saved_at (%zu bytes)\n",
                      (size_t)first.len);
    }
done:
    bytebuf_free(&first);
    bytebuf_free(&second);
    s25_fixture_remove();
}

/* registry.c #undefs its C() macro at its end, so the rows are spelled
 * out: {name, profile, rows, cols, fn, xfail_id}. */
const PtyCase yew_pty_cases[] = {
    {"trial_resume_cycles20", "modern", 24U, 80U, case_trial_resume_cycles20, NULL},
    {"trial_restore_sigkill", "modern", 24U, 80U, case_trial_restore_sigkill, NULL},
    {"trial_restore_sigsegv", "modern", 24U, 80U, case_trial_restore_sigsegv, NULL},
    {"trial_restore_hangup", "modern", 24U, 80U, case_trial_restore_hangup, NULL},
    {"trial_cross_differential", "modern", 24U, 80U, case_trial_cross_differential, NULL},
    {NULL, NULL, 0U, 0U, NULL, NULL}
};
