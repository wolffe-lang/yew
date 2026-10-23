/*
 * yw06 (R-yw06-3 = A): M-YW5's automated twins of the field boxes the
 * port can answer today — "Workspace resume in anger" (s42 §10 :495,
 * >= 20 cycles) and the restore trials of "Zero data loss" / "Terminal
 * restore in the field" (:469, :476) — written over sagitta's own PTY
 * harness at 9ace98c2 (tests/pty/harness.c, the s25 helpers of
 * tests/pty/registry.c:6230-6400); a gate of its own (tools/run-trials),
 * never a golden.
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
 *                           binary (the runner's --yew), resumed by the
 *                           OTHER (YEW_TRIAL_OTHER) and by this one from
 *                           the same saved document: both grids the
 *                           first's, both second saves byte-identical but
 *                           for `saved_at`; tools/run-trials then compares the
 *                           two directions' first saves (s25's C<->port
 *                           differential, both ways)
 *
 * Signals go only to the editor this runner spawned, inside the lane's
 * container (RULES §5). Build and run: tools/run-trials.
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
    char path[2U * PATH_MAX + 320U];
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

/* `saved_at` is the one field a save stamps (compare_live.py's rule);
 * the workspace's own `path` (four spaces in, `state_emit.c`'s layout) is
 * the run's case directory, which two runs of the runner never share. */
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
        if (!(e - i > 13U && memcmp(b->data + i, "    saved_at:", 13U) == 0) &&
            !(e - i > 9U && memcmp(b->data + i, "    path:", 9U) == 0))
            bytebuf_append(&o, b->data + i, e - i);
        i = e;
    }
    b->len = 0U;
    bytebuf_append(b, o.data, o.len);
    bytebuf_free(&o);
}

/* Writes `b` to $YEW_TRIAL_OUT/<name> when that directory is named. */
static void trial_keep(const char *name, const Bytebuf *b)
{
    const char *dir = getenv("YEW_TRIAL_OUT");
    char path[PATH_MAX];
    FILE *f;

    if (dir == NULL || dir[0] == '\0')
        return;
    (void)snprintf(path, sizeof(path), "%s/%s", dir, name);
    f = fopen(path, "wb");
    if (f == NULL)
        return;
    (void)fwrite(b->data, 1U, b->len, f);
    (void)fclose(f);
}

/* Puts `doc` back as the workspace's state.fl (the one under the
 * case's XDG_STATE_HOME). */
static bool trial_state_write(PtyCtx *c, const Bytebuf *doc)
{
    char dir[PATH_MAX];
    char path[2U * PATH_MAX + 320U];
    DIR *d;
    struct dirent *e;
    FILE *f;
    bool found = false;

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
    f = fopen(path, "wb");
    if (f == NULL)
        return false;
    (void)fwrite(doc->data, 1U, doc->len, f);
    return fclose(f) == 0;
}

/* One resume by `bin` of the saved state, checked against the first
 * process's grid, then quit; its own save read back into `out`. */
static bool trial_resume_by(PtyCtx *c, const char *bin, Bytebuf *out)
{
    c->resumed = false;
    ptc_resume(c, bin, NULL);
    ptc_settle(c, 0);
    ptc_wait_kitty_push(c, 21U);
    ptc_check_resume_exact(c);
    if (c->failed)
        return false;
    force_quit(c);
    ptc_cleanup(c);
    return trial_state_read(c, out);
}

/*
 * The arrangement built and saved by THIS binary (S1); the OTHER resumes
 * S1 and saves (S2 other); S1 put back; THIS one resumes it and saves
 * (S2 this). Each resume's grid is the first process's, exactly, and the
 * two second saves are byte-identical but for `saved_at`: the two
 * editors read S1 alike and write the same document from it. (A second
 * save differs from the first by design — restored tabs not yet visited
 * save `deferred: true` — so S1 is never compared with an S2.)
 * tools/run-trials compares the two S1 documents of the two directions.
 */
static void case_trial_cross_differential(PtyCtx *c)
{
    const char *other = getenv("YEW_TRIAL_OTHER");
    const char *tag = getenv("YEW_TRIAL_TAG");
    Bytebuf first;
    Bytebuf by_other;
    Bytebuf by_this;
    char name[64];

    if (other == NULL || other[0] == '\0') {
        ptc_check(c, false, "YEW_TRIAL_OTHER names no second editor");
        return;
    }
    if (tag == NULL || tag[0] == '\0')
        tag = "this";
    bytebuf_init(&first);
    bytebuf_init(&by_other);
    bytebuf_init(&by_this);
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
    if (!trial_resume_by(c, other, &by_other)) {
        ptc_check(c, false, "the other editor's resume or save failed");
        goto done;
    }
    if (!trial_state_write(c, &first)) {
        ptc_check(c, false, "could not put S1 back");
        goto done;
    }
    if (!trial_resume_by(c, ptc_yew_bin(c), &by_this)) {
        ptc_check(c, false, "this editor's resume or save failed");
        goto done;
    }
    /* The case's snapshot, against C's golden, on one more resume. */
    c->resumed = false;
    ptc_resume(c, ptc_yew_bin(c), NULL);
    ptc_settle(c, 0);
    ptc_wait_kitty_push(c, 21U);
    ptc_check_resume_exact(c);
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    trial_normalize(&first);
    trial_normalize(&by_other);
    trial_normalize(&by_this);
    (void)snprintf(name, sizeof(name), "%s-S1.fl", tag);
    trial_keep(name, &first);
    (void)snprintf(name, sizeof(name), "%s-S2-by-other.fl", tag);
    trial_keep(name, &by_other);
    (void)snprintf(name, sizeof(name), "%s-S2-by-this.fl", tag);
    trial_keep(name, &by_this);
    if (by_other.len != by_this.len ||
        memcmp(by_other.data, by_this.data, by_this.len) != 0) {
        ptc_check(c, false, "the two editors' second saves differ beyond saved_at");
    } else {
        (void)fprintf(stderr,
                      "trial: both editors resumed S1 to the first grid and saved %zu identical bytes\n",
                      (size_t)by_this.len);
    }
done:
    bytebuf_free(&first);
    bytebuf_free(&by_other);
    bytebuf_free(&by_this);
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
