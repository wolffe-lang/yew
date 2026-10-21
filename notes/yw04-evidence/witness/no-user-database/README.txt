yw04-shell, 2026-10-21, kasumi, wolf 0.2.33: no name service (G37). C's
`~user` (shctx), `~` completion (cmdcomp's USER source) and the login
shell fallback (job) ask getpwnam/getpwent/getpwuid, i.e. NSS. wolf
0.2.33 has std.os.users, which PARSES passwd(5) text and by design asks
no name service (its module doc); nothing in std reaches the host's
account database. The port reads /etc/passwd through std.os.users in all
three places; an account served only by LDAP, systemd-homed or macOS
Directory Services is not offered or resolved (C's answer for an unknown
user). Run: `wolf run main.lu` -> run.txt (the files source answers;
there is no other).
