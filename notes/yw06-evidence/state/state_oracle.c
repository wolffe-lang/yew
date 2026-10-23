/* Live-state differential, sagitta 9ace98c2 state_parse.c:979-1112 and
 * state_emit.c:730-820. Link only the lane's copy of pinned objects. */
#include <stdio.h>
#include <stdlib.h>
#include "edit/cmd.h"
#include "edit/ed.h"
#include "ui/layout.h"
#include "ui/tabs.h"
#include "util/buf.h"
#include "ws/state.h"
int main(int argc, char **argv) {
    if (argc != 3 && argc != 4) return 2;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    Bytebuf bytes, out; bytebuf_init(&bytes); bytebuf_init(&out);
    unsigned char chunk[65536]; size_t n;
    while ((n = fread(chunk, 1, sizeof chunk, f))) bytebuf_append(&bytes, chunk, n);
    if (ferror(f)) return 2;
    fclose(f);
    Ed ed; yew_cmd_init(); yew_ed_init(&ed);
    if (!yew_ed_open_scratch(&ed)) return 2;
    yew_layout_compute(ed.pane_root, (Rect){0, 0, 80, 24});
    int result = yew_state_apply(&ed, bytes.data, bytes.len);
    fprintf(stderr, "state_apply=%d tabs=%u\n", result, (unsigned)ed.tabs.v.len);
    if (argc == 4) {
        yew_tab_switch(&ed, 2);
        Win *w = ed.win;
        w->cs.curs.data[0].pos = BYTEOFF(3);
        w->cs.curs.data[0].anchor = BYTEOFF(4);
        w->vp.top = LINENO(5); w->vp.top_sub = 6; w->vp.left.v = 7;
        if (w->jumps.len) { w->jumps.e[0].line_hint = LINENO(8); w->jumps.e[0].stamp_ms = 9; }
        (void)yew_ed_mark_set(&ed, w->buf, (u8)'a', BYTEOFF(10));
    }
    yew_state_emit(&ed, &out);
    f = fopen(argv[2], "wb"); if (!f) return 2;
    if (fwrite(out.data, 1, out.len, f) != out.len || fclose(f)) return 2;
    yew_ed_free(&ed); bytebuf_free(&out); bytebuf_free(&bytes); yew_cmd_shutdown();
    return 0;
}
