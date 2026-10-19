# The release tier and function values (G19/G20) — witnesses

Seven programs, each `wolf build --release <dir>/main.lu` and `wolf
build <dir>/main.lu` (the native tier) at wolf 0.2.33 on kasumi,
2026-10-19. A closure passed as a `fn(str) -> (str, bool)` value:

| dir | shape | release | native |
|---|---|---|---|
| a | one file: a closure over a sibling fn, passed to a fn of the same file | green | green |
| b | one file: a closure returning its argument | green | green |
| c | one file: `fn(int) -> int` | green | green |
| d | the entry calls `lib.tier_env()`; `lib/lib.lu` makes the closure and calls it | green | green |
| e | **the entry makes the closure and passes it to `lib.tier`** | **RED**: `cannot compile this yet — a vtable slot `@main.cls0` outside this object's subset` | green |
| f | `lib/a.lu` makes the closure (its body calls `lib/b.lu`'s fn) and calls it | green | green |
| g | `lib/a.lu` makes the closure, `lib/b.lu` calls it | green | green |

The twin in the port: `term.render_new_env(caps)` — one line making the
closure inside `term` and calling `render_new` — was refused as
`@term.render_new_env.cls0` when built from `tools/demo-paint/main.lu`;
`wolf build --release --codegen-report` lists the slot under `fn main`'s
calls, so the inliner had moved the closure's making into the entry's
object (yew commits b0c5296, 385658c, 389e08b are the three refused
forms; 5bd44c1 replaces the function value with `term.Env`).
