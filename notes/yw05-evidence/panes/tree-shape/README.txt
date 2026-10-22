# yw05-panes: the tree-shape commit's gate (subject 'layout: the tree shape'), kasumi,
# wolf 0.2.34, in the container (archlinux:base-devel, the host's /usr read-only) on CPUs 12-15,
# tools/build --release and --native with warnings denied, tools/build-demo, then
# ~/lanes/yw05/bin/verify.sh's sweeps (sweep.sh: tools/goldens --suite pty --case NAME, one a case).
# The sources are the commit's tree (rsync of the worktree at that commit).

b25367a3fb8e1f0f  target/release/yew
7fb55e0e9effd3a8  target/native/yew
3d86adbf0f8e9879  target/tools/demo_paint

sweep ms1-c03-cases-native: 62/62 ok
sweep ms1-c03-cases-release: 62/62 ok
sweep ms1-c04-cases-native: 83/104 ok
sweep ms1-c04-cases-release: 83/104 ok

c04's 21 red, the same names on both tiers and yw04's 21 (R-yw04-1 20, G30 1):
s19_badge_while_running s19_exit_footer_nonzero s19_exit_footer_ok s19_exit_footer_signal s19_filter_nonzero_keeps_buffer s19_filter_replaces_region s19_filter_typeahead_replays_after_completion s19_jobs_table s19_no_output_message s19_read_at_cursor s19_stream_output s57_24_generator_pending s57_25_help_negative s57_25_help_pending s57_25_help_subcommands s57_26_fish_stub_rows s57_27_completion_follows_session s57_27_session_busy_alongside s57_27_session_cd_persists s57_27_session_exit_recovers s57_29_prompt_select_and_copy 
