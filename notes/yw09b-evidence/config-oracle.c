#define _POSIX_C_SOURCE 200809L
/* yw09b measurement, links sagitta.pin's own objects. No oracle edits.
 * Uses test_flconf.c's initialization and keymap lookup interfaces. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "edit/ed.h"
#include "edit/bind.h"
#include "edit/keymap.h"
#include "fl/flconf.h"
#include "fl/flruntime.h"
#include "fl/trace.h"
#include "fl/vm.h"

static void binding(Ed *ed, const char *seq)
{
    KeyId key;
    const Binding *b = NULL;
    (void)yew_key_parse_seq(seq, &key, 1U);
    (void)yew_keymap_lookup(&ed->bind_keys[YEW_MODE_L], &key, 1U, NULL, &b);
    printf("L %s: %s\n", seq, b == NULL ? "absent" : yew_cmd_desc(b->cmd)->name);
}
int main(int argc, char **argv)
{
    Ed ed;
    YewEdStartup startup = {0};
    Bytebuf trace;
    FlVm *vm;
    if (argc != 3) return 2;
    startup.config_path = argv[1];
    startup.trust_workspace = true;
    yew_ed_init(&ed);
    ed.ws.dir = arena_strdup(&ed.arena, argv[2]);
    if (!yew_ed_open_scratch(&ed)) return 3;
    yew_config_init(&ed, &startup);
    printf("config status: %d\n", (int)yew_config_load_all(&ed, NULL));
    printf("message: %s\n", ed.msg.text);
    binding(&ed, "X"); binding(&ed, "Y"); binding(&ed, "Z");
    vm = yew_fl_vm(&ed);
    bytebuf_init(&trace);
    fl_trace_render(vm, vm->err, &trace);
    printf("trace:\n%.*s", (int)trace.len, (const char *)trace.data);
    bytebuf_free(&trace);
    yew_ed_free(&ed);
    return 0;
}
