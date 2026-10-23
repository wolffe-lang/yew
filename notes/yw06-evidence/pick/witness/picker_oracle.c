/* C-only witness of the pinned picker (sagitta 9ace98c2), not a port and
 * not a C fix.  Links every oracle object but main.o (the finder-inputs
 * witness's shape) and drives the shipping functions:
 *   keys   W3: which keys reach the filter line (picker.c:759-870)
 *   files  W1: the file host's walk and cap (pickers.c:243-319)
 *   alloc  W5: allocation calls while the finder is drawn with its
 *          preview (picker.c:944-1093, pickers.c:166-227), counted by
 *          --wrap of the allocator over the linked objects.
 */
#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "edit/cmd.h"
#include "edit/ed.h"
#include "term/grid.h"
#include "term/input.h"
#include "ui/cmdline.h"
#include "ui/layout.h"
#include "ui/picker.h"
#include "ui/pickers.h"
#include "ui/region.h"
#include "util/arena.h"
#include "util/buf.h"

static unsigned long g_allocs;
static int g_counting;

void *__real_malloc(size_t n);
void *__real_calloc(size_t a, size_t b);
void *__real_realloc(void *p, size_t n);
void *__real_reallocarray(void *p, size_t a, size_t b);

void *__wrap_malloc(size_t n)
{
    if (g_counting)
        g_allocs++;
    return __real_malloc(n);
}

void *__wrap_calloc(size_t a, size_t b)
{
    if (g_counting)
        g_allocs++;
    return __real_calloc(a, b);
}

void *__wrap_realloc(void *p, size_t n)
{
    if (g_counting)
        g_allocs++;
    return __real_realloc(p, n);
}

void *__wrap_reallocarray(void *p, size_t a, size_t b)
{
    if (g_counting)
        g_allocs++;
    return __real_reallocarray(p, a, b);
}

static const PickItem g_items[] = {
    {"alpha.c", NULL, 1, 0U},
    {"beta.c", NULL, 2, 0U},
    {"abc.c", NULL, 3, 0U}
};

static const PickItem *items_cb(void *ctx, u32 *n)
{
    (void)ctx;
    *n = 3U;
    return g_items;
}

static void ed_make(Ed *ed, u16 rows, u16 cols, const char *dir)
{
    yew_cmd_shutdown();
    yew_cmd_init();
    yew_ed_init(ed);
    if (dir != NULL)
        ed->ws.dir = arena_strdup(&ed->arena, dir);
    if (!yew_ed_open_scratch(ed) ||
        !yew_grid_init(&ed->grid, &ed->interner, rows, cols)) {
        fputs("witness: cannot build an editor\n", stderr);
        exit(2);
    }
    ed->grid_ready = true;
    yew_layout_compute(ed->pane_root, (Rect){0U, 0U, cols, rows});
}

static void show(Ed *ed, const char *what)
{
    Bytebuf t;

    bytebuf_init(&t);
    if (ed->cmdline.active)
        yew_cmdline_text(ed, &t);
    printf("%-14s line=%s \"%.*s\" shown=%u selected=%d\n", what,
           ed->cmdline.active ? "open" : "none", (int)t.len,
           t.data == NULL ? "" : (const char *)t.data,
           (unsigned)yew_picker_shown(ed), (int)yew_picker_selected(ed));
    bytebuf_free(&t);
}

static Key key_text(char c)
{
    Key k;

    (void)memset(&k, 0, sizeof(k));
    k.kind = YEW_EV_KEY;
    k.ev = YEW_KEY_PRESS;
    k.code = (u32)(u8)c;
    k.text[0] = (u8)c;
    k.ntext = 1U;
    return k;
}

static Key key_code(u32 code, u16 mods)
{
    Key k;

    (void)memset(&k, 0, sizeof(k));
    k.kind = YEW_EV_KEY;
    k.ev = YEW_KEY_PRESS;
    k.code = code;
    k.mods = mods;
    return k;
}

static void press(Ed *ed, Key k, const char *what)
{
    bool took = yew_picker_key(ed, &k);

    printf("%-14s consumed=%d ", what, took ? 1 : 0);
    show(ed, "");
}

static int w_keys(void)
{
    Ed ed;
    PickerSpec spec;

    ed_make(&ed, 24U, 80U, NULL);
    (void)memset(&spec, 0, sizeof(spec));
    spec.title = "Witness";
    spec.items = items_cb;
    yew_picker_open(&ed, &spec);
    show(&ed, "open");
    press(&ed, key_text('a'), "a");
    press(&ed, key_text('b'), "b");
    press(&ed, key_code(YEW_KEY_BACKSPACE, 0U), "Backspace");
    press(&ed, key_code(YEW_KEY_LEFT, 0U), "Left");
    press(&ed, key_code(YEW_KEY_DELETE, 0U), "Delete");
    press(&ed, key_code((u32)'h', YEW_MOD_CTRL), "C-h");
    press(&ed, key_code((u32)'w', YEW_MOD_CTRL), "C-w");
    press(&ed, key_code((u32)'u', YEW_MOD_CTRL), "C-u");
    press(&ed, key_code((u32)'a', YEW_MOD_CTRL), "C-a");
    press(&ed, key_code(YEW_KEY_HOME, 0U), "Home");
    press(&ed, key_code(YEW_KEY_END, 0U), "End");
    press(&ed, key_code(YEW_KEY_F1, 0U), "F1");
    press(&ed, key_text('c'), "c");
    yew_picker_close(&ed, false);
    yew_ed_free(&ed);
    return 0;
}

static int make_tree(char *root, size_t cap, unsigned n)
{
    unsigned i;

    (void)snprintf(root, cap, "/tmp/yew-witness-pick-XXXXXX");
    if (mkdtemp(root) == NULL)
        return -1;
    for (i = 0U; i < n; i++) {
        char path[256];
        FILE *fp;

        (void)snprintf(path, sizeof(path), "%s/f%06u.c", root, i);
        fp = fopen(path, "wb");
        if (fp == NULL)
            return -1;
        (void)fputs("int x;\nint y;\n", fp);
        (void)fclose(fp);
    }
    return 0;
}

static void rm_tree(const char *root)
{
    char cmd[300];
    int r;

    (void)snprintf(cmd, sizeof(cmd), "rm -rf '%s'", root);
    r = system(cmd);
    (void)r;
}

static int w_files(unsigned n)
{
    char root[128];
    Ed ed;
    CmdCtx cx;
    CmdStatus st;

    if (make_tree(root, sizeof(root), n) != 0)
        return 2;
    ed_make(&ed, 24U, 80U, root);
    (void)memset(&cx, 0, sizeof(cx));
    cx.ed = &ed;
    cx.win = ed.win;
    st = yew_find_cmd_file(&cx);
    printf("files=%u status=%d active=%d total=%u shown=%u scanning_after_open=%d msg=\"%s\"\n",
           n, (int)st, yew_picker_active(&ed) ? 1 : 0,
           (unsigned)yew_picker_total(&ed), (unsigned)yew_picker_shown(&ed),
           yew_picker_scanning(&ed) ? 1 : 0,
           ed.msg.active ? ed.msg.text : "");
    yew_picker_close(&ed, false);
    yew_ed_free(&ed);
    rm_tree(root);
    return 0;
}

static int w_alloc(void)
{
    char root[128];
    Ed ed;
    CmdCtx cx;
    unsigned long before;
    int i;

    if (make_tree(root, sizeof(root), 50U) != 0)
        return 2;
    ed_make(&ed, 40U, 160U, root);
    (void)memset(&cx, 0, sizeof(cx));
    cx.ed = &ed;
    cx.win = ed.win;
    if (yew_find_cmd_file(&cx) != YEW_CMD_OK)
        return 2;
    yew_region_frame_begin();
    yew_picker_draw(&ed, (Rect){0U, 0U, 160U, 40U});
    yew_pickers_preview_reset();
    g_allocs = 0U;
    g_counting = 1;
    for (i = 0; i < 100; i++) {
        yew_region_frame_begin();
        yew_picker_draw(&ed, (Rect){0U, 0U, 160U, 40U});
    }
    g_counting = 0;
    printf("draws=100 preview_reads=%llu alloc_calls=%lu\n",
           (unsigned long long)yew_pickers_preview_reads(), g_allocs);
    before = g_allocs = 0U;
    g_counting = 1;
    for (i = 0; i < 100; i++) {
        Key k = key_code(YEW_KEY_DOWN, 0U);

        (void)yew_picker_key(&ed, &k);
    }
    g_counting = 0;
    printf("down_keys=100 alloc_calls=%lu\n", g_allocs - before);
    yew_picker_close(&ed, false);
    yew_ed_free(&ed);
    rm_tree(root);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "keys") == 0)
        return w_keys();
    if (argc == 3 && strcmp(argv[1], "files") == 0)
        return w_files((unsigned)strtoul(argv[2], NULL, 10));
    if (argc == 2 && strcmp(argv[1], "alloc") == 0)
        return w_alloc();
    fputs("usage: picker-oracle keys | files N | alloc\n", stderr);
    return 2;
}
