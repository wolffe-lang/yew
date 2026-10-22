# What the checked machine's ledger charges where native charges nothing:
# the three draws percase saw fail, and three primitives, each figure
# written to a file (wolf test shows no stdout).
cd target/hot/plantsrc
git status --short | head -3
python3 - <<'PY'
src = open('src/edit_drawbufs_test.lu').read()
i = src.index('\nfn main(')
j = src.index('\n}\n', i) + 3
body = src[:i] + '\n' + src[j:]
extra = '''
fn note(name: str, text: str) {
    fs_write_bytes("../ck-{name}.txt", bytes_of(text)) else |_| {}
}

fn test_gutter() {
    let grew = ledger_of(1, 30, false)
    note("gutter", "gutter x30 {grew}")
}

fn test_status() {
    let grew = ledger_of(2, 30, false)
    note("status", "statusline x30 {grew}")
}

fn test_idle() {
    let grew = ledger_of(4, 30, false)
    note("idle", "idle x30 {grew}")
}

fn test_cursor() {
    let grew = ledger_of(3, 30, false)
    note("cursor", "cursor x30 {grew}")
}

fn test_prim() {
    var d = 0
    var e = 0
    var f = 0
    var g = 0
    region p {
        var b = List[byte]()
        (mut b).push(1 as byte)
        (mut b).push(2 as byte)
        let _ = (mut b).pop() else 0 as byte
        let _ = (mut b).pop() else 0 as byte
        let b0 = region_bytes(p)
        var i = 0
        while i < 10 {
            (mut b).push(1 as byte)
            let _ = (mut b).pop() else 0 as byte
            i += 1
        }
        d = region_bytes(p) - b0
        let b1 = region_bytes(p)
        i = 0
        while i < 10 {
            for x in "abc".bytes() {
                if x == 0 as byte {
                    print("?")
                }
            }
            i += 1
        }
        e = region_bytes(p) - b1
        let b2 = region_bytes(p)
        i = 0
        while i < 10 {
            edit.push_dec(mut b, 1234)
            while b.len != 0 {
                let _ = (mut b).pop() else 0 as byte
            }
            i += 1
        }
        f = region_bytes(p) - b2
        var g0 = term.grid_new(4, 10)
        let blank = copy g0.blank
        term.grid_fill(mut g0, 1, 0, 10, copy blank)
        let b3 = region_bytes(p)
        i = 0
        while i < 10 {
            term.grid_fill(mut g0, 1, 0, 10, copy blank)
            i += 1
        }
        g = region_bytes(p) - b3
    }
    note("prim", "push-after-pop x10 {d}; iterate a literal's bytes x10 {e}; push_dec x10 {f}; grid_fill x10 {g}")
}
'''
open('src/zzck_hot_test.lu', 'w').write(body + extra)
PY
YEW_LOG=/dev/null ../../../.wolf-bin/wolf test --json src/zzck_hot_test.lu 2>&1 | tail -12
for f in ../ck-*.txt; do echo "$f: $(cat $f)"; done
python3 -c "import os; os.remove('src/zzck_hot_test.lu')"
git status --short | head -3
