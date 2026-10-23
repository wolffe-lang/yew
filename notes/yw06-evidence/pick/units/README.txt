The pick fork's unit evidence (kasumi ctr, taskset 8-11, wolf 0.2.34).

all-units-85aeb34.log is the record at the fork's final source head. All
seven test files are built --deny-warnings and run whole on the native
tier. Each case is then run alone on the checked machine (percase.sh,
YEW_PICK_CASE). Last, the file runs whole under tools/check-test's
checked lane (`wolf test --deny-warnings FILE`, wtest.sh).

  file                         cases  native  checked per case     check-test
  src/ws_gitignore_test.lu       26    26     26                   ok   1 s
  src/ws_walk_test.lu            20    20     20                   ok   0 s
  src/edit_groupfromdir_test.lu   7     7      7                   ok   4 s
  src/edit_narrow_test.lu        11    11      8 + 3 budget        ok  84 s
  src/edit_picker_test.lu        13    13     12 + 1 budget        ok  70 s
  src/edit_pickers_test.lu       10    10     10                   ok  47 s
  src/edit_typejump_test.lu      11    11     11                   ok   3 s

"budget" means the verdict was "unsupported" with the reason "step budget
exhausted", the yw02/yw05 precedent. These cases rest on the native run:
  - narrow 0, 4 and 5: C's 5,000-item x 10,000-trial, 20,000-item and
    50,000-item cases. narrow-case4-checked-raw.log has the machine's
    own line.
  - picker 9: the 8 MiB custom source. picker-wp-3.log has
    case-alone.sh's line: refused in 5 s.

Earlier records, kept as found:
  - finder-units-native-checked.log (46bd393): picker 9 had no verdict.
    It ran 13 min at 1.3 GB and was stopped by its pid. The text was then
    built by the builtin `repeat`, and the checked machine copies a held
    str on every inline `.bytes()[i]` (../witness/checked-bytes/run.log).
  - wtest-before.log (b886008): check-test's checked lane was RED on
    ws_walk_test.lu, case 4, trap(assert) "never loops". A 1 us step made
    no progress there. R-yw06-P2 (e932a6c) fixed it.
    edit_picker_test.lu was stopped at 980 s.
  - walk-picker-2726e35.log: walk green per case after e932a6c.
  - picker-wp-2.log (0114aab): the lent-view scan alone still left case 9
    running past 8 min. It was stopped. 5aeb34f's pushed source closes
    that.
