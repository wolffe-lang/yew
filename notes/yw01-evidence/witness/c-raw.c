/* c-raw — the C control for the mode-bit witness.
 *
 * Applies sagitta's exact raw-mode flag table (src/term/tty.c:521-543,
 * yew_tty_rawios) — the maintainer's own code (ruling #89 R1) — so the
 * witness contrasts what C yew does (ICRNL and OPOST CLEARED) with what
 * the wolf port can do through std.term (neither reachable). Clean-room
 * otherwise: no other terminal implementation is read.
 *
 *   c-raw --enter   raw, read one byte, print its decimal (cooked again)
 *   c-raw --opost   raw, write one LF, exit
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

static void rawios(struct termios *io) {
    const tcflag_t input_clear = IXON | ICRNL | INLCR | IGNCR | BRKINT |
                                 IGNBRK | PARMRK | ISTRIP | INPCK;
    const tcflag_t local_clear = ECHO | ECHONL | ICANON | ISIG | IEXTEN;
    io->c_iflag &= ~input_clear;
    io->c_oflag &= ~OPOST;
    io->c_lflag &= ~local_clear;
    io->c_cflag &= ~(CSIZE | PARENB);
    io->c_cflag |= CS8;
    io->c_cc[VMIN] = 1;
    io->c_cc[VTIME] = 0;
}

int main(int argc, char **argv) {
    struct termios saved, raw;
    if (argc != 2) return 2;
    if (tcgetattr(STDIN_FILENO, &saved) != 0) return 1;
    raw = saved;
    rawios(&raw);
    if (tcsetattr(STDIN_FILENO, TCSANOW, &raw) != 0) return 1;
    if (strcmp(argv[1], "--enter") == 0) {
        unsigned char b;
        ssize_t n = read(STDIN_FILENO, &b, 1);
        (void)tcsetattr(STDIN_FILENO, TCSANOW, &saved);
        if (n == 1) printf("%d\n", (int)b);
        else printf("eof\n");
    } else if (strcmp(argv[1], "--opost") == 0) {
        unsigned char lf = 0x0A;
        (void)!write(STDOUT_FILENO, &lf, 1);
        (void)tcsetattr(STDIN_FILENO, TCSANOW, &saved);
    } else {
        (void)tcsetattr(STDIN_FILENO, TCSANOW, &saved);
        return 2;
    }
    return 0;
}
