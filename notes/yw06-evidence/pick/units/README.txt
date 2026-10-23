The pick fork's unit evidence (kasumi ctr, taskset 8-11, wolf 0.2.34).

finder-units-native-checked.log (head 46bd393): test_narrow, test_picker,
test_pickers, test_typejump, each built --deny-warnings and run whole on
the native tier, then each case alone on the checked machine
(percase.sh, YEW_PICK_CASE). The non-exit(0) checked rows:
  narrow 0, 4, 5: "unsupported", step budget exhausted
    (narrow-case4-checked-raw.log shows the machine's line), the yw02/yw05
    precedent. These are C's 5,000-item x 10,000-trial, 20,000-item and
    50,000-item cases; they rest on the native run.
  picker 9 (picker_same_length_filter_change_refilters): no verdict. Its
    8 MiB custom-search half (test_picker.c's) ran 13 min at 1.3 GB RSS
    and 100% CPU, sharing taskset 8-11 with another fork's job, and was
    stopped by its recorded pid (3280567). It rests on the native run.
walk, gitignore and groupfromdir: ../walk-native-checked-1.log,
../finder-inputs/port-witness-and-percase.log and
../gitignore/fuzz-campaign-and-groupfromdir.log.
