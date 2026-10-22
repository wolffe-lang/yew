# The pane ratio as C's float bits (`ef7ad62`)

- `before-percase-f32.txt` — the panes fork at `6b9797b` (ratio held as
  wolf `f32`), the per-case checked run (`percase.py`): every editor case
  that lays out a tree is `unsupported \`f32\` in checked execution (f64 is
  the supported float)` — `edit_layout_test` 0 of 46 checked, `edit_draw_test`
  1 of 4, `edit_jumplist_test` 0 of 18: an `f32` ratio takes every editor
  test off the checked machine.
- `after-bits.txt` — at `ef7ad62` (the ratio as binary32 bits in an `int`,
  `util.f32`'s integer rounding): `util/f32_test` "4 cases pass" natively
  (C's twelve float-vs-double rows, a 1.8M-point grid and 200,000 random
  operands against wolf's own `f32`), its checked run `[native]` (the file
  alone uses `f32`, and 0.2.34 refuses even `f32 as f64`: "float-width
  casts (`f32`↔`f64`)"); `edit_layout_test` 45 of 46 checked-pass (one on
  the step budget), `edit_jumplist_test` 18 of 18, `edit_draw_test` 3 of 4.
- The panes gate `g3` at `ef7ad62` (`../gate-g3/`): s22's 11 on both tiers
  and the layout fuzz against C's driver.
