Checked-machine runs of the fmt fork's three test files, kasumi, lane container
(ctr.sh), wolf 0.2.35: `wolf test --deny-warnings --nocapture
--no-native-fallback FILE`, each run normal and with YEW_FL_GC_STRESS=1
(".stress"), one container per run. Each line is one run: its exit, wolf
test's verdict line, and the case lines it printed. UNSUPPORTED is the step
budget, never a pass. Scripts: ../cases.sh, ../chain.sh, ../chain2.sh,
../chain3.sh; batches: ../data-batches.txt, ../data-batches2.txt.

fmtcases.summary   src/fl_std_fmt_test.lu, YEW_FMT_CASE 0..14. Cases 1-13 PASS
                   normal and stressed. Case 0 (500-value repr round trip)
                   UNSUPPORTED both ways: allow row in tools/check-test-cases.txt;
                   native and release run it whole. Case 14 prints no case line.
mathwhole.summary  src/fl_std_math_test.lu whole: PASS normal; stressed
                   UNSUPPORTED after case 2.
mathcases.summary  the same file, YEW_MATH_CASE 0..6: 0-5 PASS normal and
                   stressed; case 6 prints no case line.
databatch.summary  src/fl_data_test.lu, YEW_DATA_FIXTURE as `|` lists. The first
                   canonical batches were too big for the budget (canonical-a
                   10 of 11 case lines, canonical-b 5 of 10 normal; with
                   a5b3e8e's single read, canonical-b stressed passed whole).
                   18-maximal-512-tabs.fl, caps/bytes and caps/nodes alone
                   UNSUPPORTED (allow rows). noncanonical 4/4, invalid 20/20,
                   caps-small (depth, string) 2/2: PASS normal and stressed.
databatch2.summary the 21 other canonical fixtures in six smaller batches
                   (c1-c6): every batch PASS normal and stressed, 21 case lines.

Tree: the fmt mirror at e36606f's code, with a5b3e8e's fl_data_test.lu copied
in before databatch's canonical-b stressed run and before databatch2. The
merged tree's native and release runs are ../tiers/merged-native-release.log.
