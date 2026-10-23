/* C-only input witness, not a port or a C fix.
 * Calls the pinned finder backend: ws/walk.c:323-381,426-561;
 * ws/gitignore.c:415-507. It never asks Git for ignore decisions.
 */
#include <stdio.h>
#include <string.h>
#include "util/arena.h"
#include "ws/gitignore.h"
#include "ws/walk.h"

int main(int argc, char **argv)
{
    FileList files;
    WalkOpts opts = {0};
    WalkState *walk;
    u64 i;

    if (argc != 2 && argc != 3)
        return 2;
    if (argc == 3) {
        Arena arena;
        GiSet *disk;
        GiSet *memory;
        char sub[4096];
        int n;

        if (strcmp(argv[2], "--scope") != 0)
            return 2;
        n = snprintf(sub, sizeof(sub), "%s/sub", argv[1]);
        if (n < 0 || (size_t)n >= sizeof(sub))
            return 2;
        arena_init(&arena);
        disk = yew_gi_load(&arena, sub, NULL);
        memory = yew_gi_compile(&arena, "sub", "/build/\n", 8U, NULL);
        printf("disk(sub/build)=%d disk(build)=%d memory-base-sub(sub/build)=%d\n",
               yew_gi_match(disk, "sub/build", true),
               yew_gi_match(disk, "build", true),
               yew_gi_match(memory, "sub/build", true));
        arena_free_all(&arena);
        return 0;
    }
    opts.use_gitignore = true;
    yew_filelist_init(&files);
    walk = yew_walk_begin(argv[1], &opts, &files);
    if (walk == NULL) {
        yew_filelist_free(&files);
        fputs("walk begin failed\n", stderr);
        return 2;
    }
    while (yew_walk_step(walk, 0)) {
    }
    for (i = 0U; i < files.paths.len; i++)
        puts(files.paths.data[i]);
    yew_walk_end(walk);
    yew_filelist_free(&files);
    return 0;
}
