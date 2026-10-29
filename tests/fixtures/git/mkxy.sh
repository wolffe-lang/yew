#!/bin/sh
# mkxy.sh DEST: the records `mkrepo.sh`'s fixture (sagitta's, copied
# beside this file) does not reach, built by real git (yw13, s51's
# grammar): DEST/xy holds all seven unmerged XY pairs mid-merge; DEST/mix
# holds a copy, an intent-to-add, staged and worktree deletions, a
# typechange, a submodule in each of its states, ignored files and
# directories, and paths that are not UTF-8. Deterministic as mkrepo.sh
# is: no host git configuration, fixed identities and dates.
set -eu
CDPATH=
export CDPATH

if ! command -v git >/dev/null 2>&1; then
    echo "HARNESS_SKIP git fixture: git not found"
    exit 0
fi
if [ "$#" -ne 1 ]; then
    echo "usage: $0 DEST" >&2
    exit 2
fi
dest=$1
if [ -e "$dest" ]; then
    echo "mkxy.sh: destination already exists: $dest" >&2
    exit 2
fi

unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
unset GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE
unset GIT_CONFIG_COUNT GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0
unset GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_DEFAULT_HASH GIT_DEFAULT_REF_FORMAT
unset GIT_TEMPLATE_DIR
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_AUTHOR_NAME='Yew Fixture'
export GIT_AUTHOR_EMAIL='fixture@yew.invalid'
export GIT_AUTHOR_DATE='2001-01-01T00:00:00 +0000'
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
export LC_ALL=C
export TZ=UTC
umask 022

git_init()
{
    mkdir -p "$1"
    (
        cd "$1"
        git -c init.defaultBranch=trunk \
            -c init.defaultObjectFormat=sha1 init -q
        git symbolic-ref HEAD refs/heads/trunk
        git config user.name "$GIT_AUTHOR_NAME"
        git config user.email "$GIT_AUTHOR_EMAIL"
        git config commit.gpgsign false
        git config core.autocrlf false
        git config core.filemode false
        git config core.quotepath false
        git config core.hooksPath .git/no-hooks
        git config status.renames true
        git config merge.conflictstyle merge
        git config protocol.file.allow always
    )
}

mkdir -p "$dest"
dest_abs=$(cd "$dest" && pwd)

# --- every unmerged XY ------------------------------------------------
# UU both modified, AA both added, UD modified here and deleted there, DU
# deleted here and modified there, and the rename/rename(1to2) triple:
# DD for the source both sides renamed, AU and UA for the two new names.
git_init "$dest_abs/xy"
(
    cd "$dest_abs/xy"
    printf 'uu base\n' >uu.txt
    printf 'ud base\n' >ud.txt
    printf 'du base\n' >du.txt
    printf 'renamed both ways\nline two\nline three\n' >rr.txt
    git add -- .
    git commit -q -m 'xy base'
    git checkout -q -b theirs
    printf 'uu theirs\n' >uu.txt
    git rm -q -- ud.txt
    printf 'du theirs\n' >du.txt
    git mv -- rr.txt rr-theirs.txt
    printf 'aa theirs\n' >aa.txt
    git add -- .
    git commit -q -m 'xy theirs'
    git checkout -q trunk
    printf 'uu ours\n' >uu.txt
    printf 'ud ours\n' >ud.txt
    git rm -q -- du.txt
    git mv -- rr.txt rr-ours.txt
    printf 'aa ours\n' >aa.txt
    git add -- .
    git commit -q -m 'xy ours'
    if git merge --no-edit theirs >/dev/null 2>&1; then
        echo "mkxy.sh: expected merge conflicts were not produced" >&2
        exit 1
    fi
)

# --- the rest of the grammar --------------------------------------------
git_init "$dest_abs/subsrc"
(
    cd "$dest_abs/subsrc"
    printf 'in the submodule\n' >inner.txt
    git add -- inner.txt
    git commit -q -m 'submodule base'
)
git_init "$dest_abs/mix"
(
    cd "$dest_abs/mix"
    printf '/ignored.log\n/ignored-dir/\n*.tmp\n' >.gitignore
    printf 'copy source payload\nwith lines\nenough to match\n' >copy-src.txt
    printf 'deleted in the worktree\n' >gone-worktree.txt
    printf 'deleted in the index\n' >gone-index.txt
    printf 'regular before symlink\n' >typechange.txt
    printf 'bytes\n' >"$(printf 'bad\376name.txt')"
    git add -- .
    git -c protocol.file.allow=always submodule add -q ../subsrc sub \
        >/dev/null 2>&1
    git commit -q -m 'mix base'
    # A copy, found because its source changed in the same change set.
    cp copy-src.txt copy-dst.txt
    printf 'one more line\n' >>copy-src.txt
    git add -- copy-src.txt copy-dst.txt
    # Intent to add: `.A` with no index object.
    printf 'intent\n' >intent.txt
    git add -N -- intent.txt
    rm gone-worktree.txt
    git rm -q -- gone-index.txt
    rm typechange.txt
    ln -s copy-src.txt typechange.txt
    git add -- typechange.txt
    # A non-UTF-8 path renamed in the index, and one left untracked.
    git mv -- "$(printf 'bad\376name.txt')" "$(printf 'bad\375renamed.txt')"
    printf 'untracked bytes\n' >"$(printf 'raw\377.txt')"
    printf 'untracked\n' >untracked.txt
    printf 'ignored\n' >ignored.log
    mkdir ignored-dir
    printf 'deep\n' >ignored-dir/deep.txt
    printf 'scratch\n' >scratch.tmp
    # The submodule: a new commit (C), a modified tracked file (M) and an
    # untracked one (U) inside it.
    (
        cd sub
        git config user.name "$GIT_AUTHOR_NAME"
        git config user.email "$GIT_AUTHOR_EMAIL"
        git config commit.gpgsign false
        printf 'advanced\n' >advance.txt
        git add -- advance.txt
        git commit -q -m 'submodule advance'
        printf 'modified inside\n' >>inner.txt
        printf 'untracked inside\n' >loose.txt
    )
)
