set -u
o=$1
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
run() { tag=$1; shift; s=$(date +%s); "$@" $W conform-run --deny-warnings --checked --json src/edit_cmdcomp_shell_test.lu > $o/$tag.json 2> $o/$tag.err; echo "$tag rc=$? secs=$(( $(date +%s) - s )) $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict"), "|", d.get("trap_message") or d.get("x-unsupported-construct") or "")' $o/$tag.json 2>&1 | head -c 300)" >> $o/summary.txt; }
: > $o/summary.txt
run plain taskset -c 8
run plain2 taskset -c 8
( taskset -c 8 sh -c 'while :; do :; done' & echo $! > $o/hog1; taskset -c 8 sh -c 'while :; do :; done' & echo $! > $o/hog2; wait ) &
sleep 1
run hogged taskset -c 8
run hogged2 taskset -c 8
kill $(cat $o/hog1) $(cat $o/hog2) 2>/dev/null
echo done >> $o/summary.txt
