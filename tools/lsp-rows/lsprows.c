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
 * yw11b's rows, over `wolf lsp`:
 *
 *   lspw_goto_def      ed.lsp.goto_def from a call to its definition
 *   lspw_goto_def_file the definition in the package's other file, opened
 *   lspw_goto_unsupported  ed.lsp.goto_decl: wolf lsp has no declaration
 *   lspw_references    the two-row references picker, then closed
 *   lspw_symbols       the document symbol picker
 *   lspw_hover         the hover panel below the definition's name, then
 *                      esc
 *   lspw_rename        g R: the prompt, the summary panel, applied
 *
 * and over the fake server's feature modes:
 *
 *   lspf_null          null definition, hover and symbols: the sentences
 *   lspf_error         error replies dropped silently
 *   lspf_stale         a hover answered after the document changed
 *   lspf_deadline      a definition answered past its deadline: ignored
 *   lspf_partial       one capability: the others refused by name
 *   lspf_highlight     read and write highlights after the idle wait
 *   lspf_signature     "(" typed: the signature panel above the cursor
 *   lspf_rename_files  a rename over the open file and one not open: the
 *                      summary, then applied to both buffers
 *
 * and C's own rename sessions (tests/pty/registry.c's s47 cases), whose
 * goldens also hold the document's syntax colouring (yw10's):
 *
 *   lspg_rename_summary      the summary panel over a dirty file
 *   lspg_rename_apply        Enter: applied, the sentence
 *   lspg_rename_unknown_key  another key closes the confirmation
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

/* A wait that failed prints the screen it gave up on (the snapshot's text
 * section, the cursor first), so a red row says what it saw. */
static void lsprow_show_failure(PtyCtx *c)
{
    static const PtyCase *shown_test;
    static unsigned shown_run;
    Bytebuf screen;
    const char *text;
    const char *style;

    /* Once a run: the waits after the first failure fail at once. */
    if (!c->failed || (shown_test == c->test && shown_run == lsprow_run))
        return;
    shown_test = c->test;
    shown_run = lsprow_run;
    bytebuf_init(&screen);
    snapshot_write(&c->vt, &screen);
    bytebuf_push_u8(&screen, 0U);
    text = strstr((const char *)screen.data, "--- text\n");
    style = text != NULL ? strstr(text, "--- style") : NULL;
    (void)fprintf(stderr, "lsp-row: %s: the screen (cursor row %d, column %d):\n",
                  c->test->name, c->vt.cur_r, c->vt.cur_c);
    if (text != NULL && style != NULL)
        (void)fprintf(stderr, "%.*s", (int)(style - text), text);
    bytebuf_free(&screen);
}

static void lsprow_wait(PtyCtx *c, const char *text, const char *failure)
{
    s47_wait_screen(c, text, failure);
    lsprow_show_failure(c);
    ptc_settle(c, LSPROW_QUIET_MS);
}

static bool lsprow_screen_lacks(const PtyCtx *c, const void *arg)
{
    return !s43_screen_contains(&c->vt, (const char *)arg);
}

static void lsprow_wait_gone(PtyCtx *c, const char *text, const char *failure)
{
    ptc_wait_until(c, lsprow_screen_lacks, text, failure);
    lsprow_show_failure(c);
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
    /* The list's count, not a blind settle: a slow host can leave a quiet
     * gap between the picker's frame and its populated list. */
    lsprow_wait(c, "1/1", "the diagnostic list never showed its one row");
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

/* ---- yw11b: the features ------------------------------------------- */

/* The server's badge without its ellipsis: initialize answered. The badge
 * can lag a completed handshake until another event repaints it
 * (registry.c:9886-9888 says so of C), so a quiet ESC (nothing in N mode)
 * is the repaint the wait asks for. */
static bool lsprow_badge_ready(const PtyCtx *c, const void *arg)
{
    char busy[64];

    (void)snprintf(busy, sizeof(busy), "%s\xe2\x80\xa6", (const char *)arg);
    return s43_screen_contains(&c->vt, (const char *)arg) &&
           !s43_screen_contains(&c->vt, busy);
}

static void lsprow_wait_ready(PtyCtx *c, const char *id)
{
    int tries;

    s47_wait_screen(c, id, "the server never showed on the statusline");
    for (tries = 0; tries < 40 && !c->failed && !lsprow_badge_ready(c, id);
         tries++) {
        ptc_keys(c, "esc");
        ptc_settle(c, 250);
    }
    ptc_check(c, lsprow_badge_ready(c, id), "the server never became ready");
    lsprow_show_failure(c);
    ptc_settle(c, LSPROW_QUIET_MS);
}


static const char lsprow_calls[] =
    "fn add(a: int, b: int) -> int {\n"
    "    a + b\n"
    "}\n"
    "\n"
    "fn main() -> int {\n"
    "    add(1, 2)\n"
    "}\n";

static const char lsprow_twice_main[] =
    "fn main() -> int {\n"
    "    twice(4)\n"
    "}\n";

static const char lsprow_twice_util[] =
    "fn twice(x: int) -> int {\n"
    "    x * 2\n"
    "}\n";

static bool lsprow_cursor_on_row(const PtyCtx *c, const void *arg)
{
    return c->vt.cur_r == *(const int *)arg;
}

/* The cursor on screen row ROW (row 0 is the tab strip). */
static void lsprow_wait_row(PtyCtx *c, int row, const char *failure)
{
    ptc_wait_until(c, lsprow_cursor_on_row, &row, failure);
    lsprow_show_failure(c);
    ptc_settle(c, LSPROW_QUIET_MS);
}

/* The rows' gutter (compare.py's GUTTER): text column 0 is screen column
 * 6, and screen row 0 is the tab strip, so line N is screen row N. */
#define LSPROW_GUTTER 6

static bool lsprow_color_eq(YewColor a, YewColor b)
{
    return a.tag == b.tag &&
           (a.tag == YEW_COLOR_DEFAULT ||
            (a.r == b.r && a.g == b.g && a.b == b.b));
}

/* The cell at ROW, COL carries a mark the cell at ROW, PLAIN lacks: a
 * background or an underline, which on these rows' text only an overlay
 * sets (draw.c:606-639). */
static bool lsprow_cell_marked(const VtScreen *vt, int row, int col,
                               int plain)
{
    const VtCell *a;
    const VtCell *b;

    if (row < 0 || row >= vt->rows || col < 0 || col >= vt->cols ||
        plain < 0 || plain >= vt->cols || vt->cells == NULL)
        return false;
    a = &vt->cells[(size_t)row * (size_t)vt->cols + (size_t)col];
    b = &vt->cells[(size_t)row * (size_t)vt->cols + (size_t)plain];
    return !lsprow_color_eq(a->bg, b->bg) ||
           ((a->attrs ^ b->attrs) & YEW_ATTR_UNDERLINE) != 0;
}

/* Both of the fake's highlights drawn (fakeserver.py's `highlight`: line
 * 1's characters 0-2 and line 2's 4-5), each against a cell of its own
 * line outside it. Which span is the read and which the write is the
 * comparison's to hold, cell for cell: this waits on the frame only. */
static bool lsprow_highlit(const PtyCtx *c, const void *arg)
{
    (void)arg;
    return lsprow_cell_marked(&c->vt, 1, LSPROW_GUTTER + 0,
                              LSPROW_GUTTER + 3) &&
           lsprow_cell_marked(&c->vt, 2, LSPROW_GUTTER + 4,
                              LSPROW_GUTTER + 6);
}

static void lsprow_wait_highlit(PtyCtx *c, const char *failure)
{
    ptc_wait_until(c, lsprow_highlit, NULL, failure);
    lsprow_show_failure(c);
    ptc_settle(c, LSPROW_QUIET_MS);
}

/* The cursor at LINE:COL (1-based) by the statusline's position field:
 * each step of a row's walk is waited for, so a busy host cannot fold the
 * next command line into the last one. */
static void lsprow_wait_pos(PtyCtx *c, int line, int col)
{
    char pos[32];

    (void)snprintf(pos, sizeof(pos), "lf  %d:%d  ", line, col);
    lsprow_wait(c, pos, "the cursor did not reach its position");
}

/* N graphemes right from LINE:COL, one command each: the arrows move by
 * the mode's unit (L, a line: `<right>` is its end, runtime/init.fl:53),
 * and the rows need a column. */
static void lsprow_char_right(PtyCtx *c, int line, int col, int n)
{
    int i;

    for (i = 1; i <= n; i++) {
        lsprow_command(c, "ed.move.char.right");
        lsprow_wait_pos(c, line, col + i);
    }
}

/* On the call `add(1, 2)`: line 6, column 5 (1-based). */
static void lsprow_to_call(PtyCtx *c)
{
    ptc_keys(c, "down down down down down");
    lsprow_wait_pos(c, 6, 1);
    lsprow_char_right(c, 6, 1, 4);
}

static void case_lspw_goto_def(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    lsprow_to_call(c);
    lsprow_dump(c, "1-call");
    lsprow_command(c, "ed.lsp.goto_def");
    lsprow_wait_row(c, 1, "goto_def did not reach add's definition");
    lsprow_dump(c, "2-def");
    force_quit(c);
}

static void case_lspw_goto_def_file(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_twice_main) ||
        !lsprow_write(c, "src/util.lu", lsprow_twice_util))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    ptc_keys(c, "down");
    lsprow_wait_pos(c, 2, 1);
    lsprow_char_right(c, 2, 1, 4);
    lsprow_command(c, "ed.lsp.goto_def");
    lsprow_wait(c, "x * 2", "goto_def did not open the other file");
    lsprow_dump(c, "1-util");
    force_quit(c);
}

static void case_lspw_goto_unsupported(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    lsprow_to_call(c);
    lsprow_command(c, "ed.lsp.goto_decl");
    lsprow_wait(c, "wolf does not support declaration",
                "goto_decl did not say the capability is missing");
    lsprow_dump(c, "1-decl");
    force_quit(c);
}

static void case_lspw_references(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    lsprow_char_right(c, 1, 1, 3);
    lsprow_command(c, "ed.lsp.references");
    lsprow_wait(c, "2/2", "the references picker never showed two rows");
    lsprow_dump(c, "1-picker");
    ptc_keys(c, "esc");
    lsprow_wait_gone(c, "up/down move", "esc did not close the references picker");
    lsprow_dump(c, "2-closed");
    force_quit(c);
}

static void case_lspw_symbols(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    lsprow_command(c, "ed.lsp.symbols");
    lsprow_wait(c, "2/2", "the symbol picker never showed two rows");
    lsprow_dump(c, "1-picker");
    ptc_keys(c, "esc");
    lsprow_wait_gone(c, "up/down move", "esc did not close the symbol picker");
    force_quit(c);
}

static void case_lspw_hover(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    /* On the definition's name: wolf lsp answers `fn add` there (on the
     * call it answers the call's type). The document holds that text
     * too, so the wait is on the panel's title with its corner: the typed
     * command line (`:ed.lsp.hover`) holds the bare word, and a wait on it
     * could pass before the command ran. */
    lsprow_char_right(c, 1, 1, 3);
    lsprow_command(c, "ed.lsp.hover");
    lsprow_wait(c, "\xe2\x94\x8c hover", "the hover panel never opened");
    lsprow_dump(c, "1-panel");
    ptc_keys(c, "esc");
    lsprow_wait_gone(c, "\xe2\x94\x8c hover", "esc did not close the hover panel");
    lsprow_dump(c, "2-closed");
    force_quit(c);
}

static void case_lspw_rename(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open(c);
    lsprow_wait_ready(c, "wolf");
    lsprow_char_right(c, 1, 1, 3);
    ptc_keys(c, "g R");
    lsprow_wait(c, ":add", "the rename prompt never showed the old name");
    ptc_keys(c, "ctrl+u");
    ptc_bytes(c, "plus");
    lsprow_wait(c, ":plus", "the new name was not typed");
    ptc_keys(c, "enter");
    lsprow_wait(c, "rename 'add' \xE2\x86\x92 'plus'",
                "the rename summary never showed");
    lsprow_dump(c, "1-summary");
    ptc_keys(c, "enter");
    lsprow_wait(c, "renamed ", "the rename was not applied");
    ptc_check(c, s43_screen_contains(&c->vt, "plus(1, 2)"),
              "the call was not renamed");
    lsprow_dump(c, "2-applied");
    force_quit(c);
}

static void case_lspf_null(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "null", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_to_call(c);
    lsprow_command(c, "ed.lsp.goto_def");
    lsprow_wait(c, "fake: no definition found",
                "a null definition did not say so");
    lsprow_dump(c, "1-def");
    lsprow_command(c, "ed.lsp.hover");
    lsprow_wait(c, "no hover information here", "a null hover did not say so");
    lsprow_dump(c, "2-hover");
    lsprow_command(c, "ed.lsp.symbols");
    lsprow_wait(c, "fake: no document symbols found",
                "null symbols did not say so");
    lsprow_dump(c, "3-symbols");
    force_quit(c);
}

/* The fake's answers that the editor shows nothing for are each followed
 * by a receipt (fakeserver.py): one more warning on line 1, read after
 * the answer on the same pipe. A row that holds such an answer silent
 * waits for the badge, W:N after the Nth, never for a quiet gap. */
static void lsprow_wait_receipt(PtyCtx *c, int n, const char *failure)
{
    char badge[16];

    (void)snprintf(badge, sizeof(badge), "W:%d", n);
    lsprow_wait(c, badge, failure);
}

static void case_lspf_error(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "error", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_to_call(c);
    /* An error reply other than -32601 is dropped silently, its
     * capability kept (features.c:1630-1634, :1804-1808). */
    lsprow_command(c, "ed.lsp.hover");
    lsprow_wait_receipt(c, 1, "the hover's error reply never came");
    ptc_check(c, !s43_screen_contains(&c->vt, "boom") &&
                     !s43_screen_contains(&c->vt, "\xe2\x94\x8c hover"),
              "an error reply to hover was shown");
    lsprow_dump(c, "1-hover");
    lsprow_command(c, "ed.lsp.references");
    lsprow_wait_receipt(c, 2, "the references' error reply never came");
    ptc_check(c, !s43_screen_contains(&c->vt, "boom") &&
                     !s43_screen_contains(&c->vt, "up/down move"),
              "an error reply opened a picker");
    lsprow_dump(c, "2-references");
    force_quit(c);
}

static void case_lspf_stale(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "stale", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_to_call(c);
    lsprow_command(c, "ed.lsp.hover");
    /* The fake answers only once the document has changed, so the reply
     * answers an older generation and is dropped before its callback
     * (client.c:857-877). */
    ptc_keys(c, "i z esc");
    lsprow_wait(c, "zadd(1, 2)", "the edit did not land");
    lsprow_wait_receipt(c, 1, "the late hover reply never came");
    ptc_check(c, !s43_screen_contains(&c->vt, "late"),
              "a reply for a changed document was shown");
    lsprow_dump(c, "1-dropped");
    force_quit(c);
}

static bool lsprow_fake_marked(const PtyCtx *c, const void *arg)
{
    char path[PATH_MAX];
    int n = snprintf(path, sizeof(path), "%s/fake.marker", c->state_dir);

    (void)arg;
    return n > 0 && (size_t)n < sizeof(path) && access(path, F_OK) == 0;
}

static void case_lspf_deadline(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "deadline", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_to_call(c);
    lsprow_command(c, "ed.lsp.goto_def");
    /* The request at the fake (its marker), the command line closed. */
    ptc_wait_until(c, lsprow_fake_marked, NULL,
                   "the definition request never reached the fake");
    lsprow_wait_gone(c, ":ed.lsp.goto_def", "the command line stayed open");
    lsprow_dump(c, "1-pending");
    /* The answer comes 12 s after the request, past its 10 s deadline
     * (jsonrpc.h:20): the sweep has already called the request back with
     * the timeout error (jsonrpc.c:682-718), so the answer's id is no
     * longer pending and it is ignored. Nothing is said, nothing moves. */
    lsprow_wait_receipt(c, 1, "the late definition reply never came");
    ptc_check(c, c->vt.cur_r == 6U,
              "a definition answered past its deadline moved the cursor");
    lsprow_dump(c, "2-expired");
    force_quit(c);
}

static void case_lspf_partial(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "partial", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_to_call(c);
    lsprow_command(c, "ed.lsp.hover");
    lsprow_wait(c, "fake does not support hover",
                "an absent hover did not say so");
    lsprow_dump(c, "1-hover");
    /* A refused command keeps its line open for an edit: ESC closes it. */
    ptc_keys(c, "esc");
    lsprow_wait_gone(c, ":ed.lsp.hover", "esc did not close the refused command");
    lsprow_command(c, "ed.lsp.goto_def");
    lsprow_wait_row(c, 1, "the one capability did not answer");
    lsprow_dump(c, "2-def");
    force_quit(c);
}

static void case_lspf_highlight(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "highlight", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_char_right(c, 1, 1, 1);
    /* The idle 300 ms (highlight.c:17), the reply, the frame. */
    lsprow_wait_highlit(c, "the highlights never showed after the idle");
    lsprow_dump(c, "1-highlit");
    ptc_keys(c, "i z esc");
    /* The edit moves the buffer's generation, which drops both spans
     * (draw.c:646-648); the cursor then stops again, and after the idle
     * the server's answer for the edited text is drawn. The kept screen
     * is that one, waited for: a quiet gap after the edit would race the
     * idle timer. */
    lsprow_wait(c, "fzn add", "the edit did not land");
    lsprow_wait_highlit(c, "the highlights never came back after the edit");
    lsprow_dump(c, "2-edited");
    force_quit(c);
}

static void case_lspf_signature(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls))
        return;
    lsprow_open_fake(c, "signature", 30000);
    lsprow_wait_ready(c, "fake");
    ptc_keys(c, "down down down down down end i");
    ptc_settle(c, 0);
    ptc_bytes(c, " add(");
    lsprow_wait(c, "plus(x: int, y: int)", "the signature panel never showed");
    lsprow_dump(c, "1-panel");
    ptc_keys(c, "esc");
    lsprow_wait_gone(c, "plus(x: int, y: int)", "esc did not close the signature panel");
    lsprow_dump(c, "2-closed");
    force_quit(c);
}

static const char lsprow_other[] =
    "fn add_one(x: int) -> int {\n"
    "    add(x, 1)\n"
    "}\n";

static void case_lspf_rename_files(PtyCtx *c)
{
    if (!lsprow_package(c, lsprow_calls) ||
        !lsprow_write(c, "src/other.lu", lsprow_other))
        return;
    lsprow_open_fake(c, "renamefiles", 30000);
    lsprow_wait_ready(c, "fake");
    lsprow_char_right(c, 1, 1, 3);
    ptc_keys(c, "g R");
    lsprow_wait(c, ":add", "the rename prompt never showed the old name");
    ptc_keys(c, "ctrl+u");
    ptc_bytes(c, "sum");
    lsprow_wait(c, ":sum", "the new name was not typed");
    ptc_keys(c, "enter");
    lsprow_wait(c, "rename 'add' \xE2\x86\x92 'sum'",
                "the rename summary never showed");
    lsprow_dump(c, "1-summary");
    ptc_keys(c, "enter");
    lsprow_wait(c, "renamed ", "the rename was not applied");
    ptc_check(c, s43_screen_contains(&c->vt, "sum(1, 2)"),
              "the open file's call was not renamed");
    lsprow_dump(c, "2-applied");
    force_quit(c);
}

/* C's own s47 rename sessions (registry.c:9820-10042: fakelsp beside the
 * editor binary, `alpha.c` made dirty first), kept as screens instead of
 * held to a golden: the goldens also hold the document's syntax colouring
 * (the typed `!` is C's operator colour), which is yw10's, and these rows
 * compare everything else. After KEYS the row waits for WAIT to show or
 * for GONE to leave (the panel's key hint: C's own unknown-key check,
 * registry.c:10014-10016). */
static void lsprow_s47(PtyCtx *c, const char *keys, const char *wait,
                       const char *gone, const char *label)
{
    S47RenameFix f;

    if (!s47_rename_open(c, "session-rename", &f))
        return;
    s47_rename_begin(c, true, "rename 'alpha' \xE2\x86\x92 'beta'");
    if (keys != NULL)
        ptc_keys(c, keys);
    if (wait != NULL)
        lsprow_wait(c, wait, "the rename answer did not show");
    else
        lsprow_wait_gone(c, gone, "the rename confirmation stayed open");
    lsprow_dump(c, label);
    s47_rename_finish(c, &f);
}

/* s47_rename_begin waited for the summary's title; the summary's last
 * line is the key hint. */
static void case_lspg_rename_summary(PtyCtx *c)
{
    lsprow_s47(c, NULL, "enter apply", NULL, "1-summary");
}

static void case_lspg_rename_apply(PtyCtx *c)
{
    lsprow_s47(c, "enter", "renamed ", NULL, "1-applied");
}

static void case_lspg_rename_unknown_key(PtyCtx *c)
{
    lsprow_s47(c, "left", NULL, "enter apply", "1-left");
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
    {"lspw_goto_def", "modern", 24U, 80U, case_lspw_goto_def, NULL},
    {"lspw_goto_def_file", "modern", 24U, 80U, case_lspw_goto_def_file, NULL},
    {"lspw_goto_unsupported", "modern", 24U, 80U, case_lspw_goto_unsupported, NULL},
    {"lspw_references", "modern", 24U, 80U, case_lspw_references, NULL},
    {"lspw_symbols", "modern", 24U, 80U, case_lspw_symbols, NULL},
    {"lspw_hover", "modern", 24U, 80U, case_lspw_hover, NULL},
    {"lspw_rename", "modern", 24U, 80U, case_lspw_rename, NULL},
    {"lspf_null", "modern", 24U, 80U, case_lspf_null, NULL},
    {"lspf_error", "modern", 24U, 80U, case_lspf_error, NULL},
    {"lspf_stale", "modern", 24U, 80U, case_lspf_stale, NULL},
    {"lspf_deadline", "modern", 24U, 80U, case_lspf_deadline, NULL},
    {"lspf_partial", "modern", 24U, 80U, case_lspf_partial, NULL},
    {"lspf_highlight", "modern", 24U, 80U, case_lspf_highlight, NULL},
    {"lspf_signature", "modern", 24U, 80U, case_lspf_signature, NULL},
    {"lspf_rename_files", "modern", 24U, 80U, case_lspf_rename_files, NULL},
    {"lspg_rename_summary", "modern", 24U, 80U, case_lspg_rename_summary, NULL},
    {"lspg_rename_apply", "modern", 24U, 80U, case_lspg_rename_apply, NULL},
    {"lspg_rename_unknown_key", "modern", 24U, 80U, case_lspg_rename_unknown_key, NULL},
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
