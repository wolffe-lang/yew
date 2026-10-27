/*
 * yw09 nested-eval witness (R-yw09-6), linked against sagitta 9ace98c2's
 * own objects; nothing here is filed in sagitta.
 *
 * The question: what origin does `ed.fl.eval`, reached through `ed.run`
 * from a frame whose origin is NOT the user config, compile its source
 * with? fl_runtime_eval (src/fl/fleval.c:263-302) always compiles with
 * runtime_origin() (fleval.c:30-33: CONFIG, FL_CAP_ALL), and
 * command_caps (src/fl/flapi.c:1911-1933) has no row for ed.fl.eval, so
 * fl_cap_origin (src/fl/origin.c:207-228) answers CONFIG/ALL inside the
 * nested chunk.
 *
 * The outer frames are set up the way tests/unit/test_fl_runtime.c:474-
 * 477 sets one: a chunk compiled by fl_compile_str, its fn->origin then
 * given a narrower kind and capability set, and vm->root_origin the same.
 *
 *   A  the restricted frame runs ed.buf.open itself      (needs fs.read)
 *   B  the restricted frame runs it inside ed.fl.eval
 *   C  the restricted frame registers on("ed.idle") itself
 *   D  the restricted frame registers it inside ed.fl.eval
 *
 * Each line printed is one observation; nothing is asserted, so the
 * output is the evidence (notes/yw09-evidence/nested-eval/c.txt).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "edit/ed.h"
#include "fl/flruntime.h"
#include "fl/flruntime_int.h"
#include "fl/origin.h"
#include "fl/trace.h"
#include "fl/vm.h"
#include "util/buf.h"

static FlOrigin narrow(void)
{
    return (FlOrigin){(u8)FL_ORIGIN_WORKSPACE, 0U, 0U, 0U};
}

static void run(Ed *ed, const char *tag, const char *source)
{
    FlVm *vm = yew_fl_vm(ed);
    FlFn *fn = fl_compile_str(ed->fl, (const u8 *)source, strlen(source),
                              "<witness>");
    FlValue result = FL_NIL_V;
    CmdSource saved;
    u32 nbufs = ed->ws.nbufs;
    u32 nhooks = ed->hooks.n;
    bool ok;

    if (fn == NULL) {
        printf("%s: compile failed\n", tag);
        return;
    }
    fn->origin = narrow();
    vm->root_origin = narrow();
    saved = ed->fl->command_source;
    ed->fl->command_source = YEW_SRC_FLETCH;
    ok = fl_vm_run(vm, fn, &result);
    ed->fl->command_source = saved;
    vm->root_origin = (FlOrigin){(u8)FL_ORIGIN_CONFIG, 0U, FL_CAP_ALL, 0U};
    printf("%s: ok=%d buffers %u->%u hooks %u->%u", tag, ok ? 1 : 0,
           (unsigned)nbufs, (unsigned)ed->ws.nbufs, (unsigned)nhooks,
           (unsigned)ed->hooks.n);
    if (ed->hooks.n > nhooks) {
        u32 o = ed->hooks.v[ed->hooks.n - 1U].origin;

        printf(" last-hook-origin=%u", (unsigned)o);
        if (o < ed->origins.n)
            printf(" kind=%u caps=%u", (unsigned)ed->origins.v[o].kind,
                   (unsigned)ed->origins.v[o].caps);
    }
    if (!ok) {
        Bytebuf trace;
        size_t i;

        bytebuf_init(&trace);
        fl_trace_render(vm, result, &trace);
        printf(" error=");
        for (i = 0U; i < trace.len && trace.data[i] != '\n'; i++)
            putchar(trace.data[i]);
        bytebuf_free(&trace);
    }
    printf("\n");
}

int main(void)
{
    const char *tmp = getenv("TMPDIR");
    char a[4096];
    char b[4096];
    char src[8192];
    Ed ed;

    if (tmp == NULL)
        tmp = "/tmp";
    (void)snprintf(a, sizeof(a), "%s/yw09-nested-eval-a.txt", tmp);
    (void)snprintf(b, sizeof(b), "%s/yw09-nested-eval-b.txt", tmp);
    yew_ed_init(&ed);
    if (!yew_ed_open_scratch(&ed)) {
        printf("open_scratch failed\n");
        return 1;
    }
    printf("restricted frame: kind=%u (FL_ORIGIN_WORKSPACE) caps=0\n",
           (unsigned)FL_ORIGIN_WORKSPACE);
    (void)snprintf(src, sizeof(src),
                   "import ed\ned.run(\"ed.buf.open\", {\"sarg\": \"%s\"})\n",
                   a);
    run(&ed, "A direct ed.buf.open", src);
    (void)snprintf(src, sizeof(src),
                   "import ed\ned.run(\"ed.fl.eval\", {\"sarg\": "
                   "\"import ed\\ned.run(\\\"ed.buf.open\\\", "
                   "{\\\"sarg\\\": \\\"%s\\\"})\"})\n",
                   b);
    run(&ed, "B nested ed.buf.open", src);
    run(&ed, "C direct on(ed.idle)",
        "on(\"ed.idle\", fn() { nil })\n");
    run(&ed, "D nested on(ed.idle)",
        "import ed\ned.run(\"ed.fl.eval\", {\"sarg\": "
        "\"on(\\\"ed.idle\\\", fn() { nil })\"})\n");
    yew_ed_free(&ed);
    return 0;
}
