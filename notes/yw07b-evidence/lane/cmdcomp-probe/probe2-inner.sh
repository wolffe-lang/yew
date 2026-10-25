set -u
o=$1
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
: > $o/summary.txt
for n in 8 16; do
  pids=""
  for k in $(seq 1 $n); do taskset -c 8 sh -c 'while :; do :; done' & pids="$pids $!"; done
  sleep 1
  s=$(date +%s)
  taskset -c 8 $W conform-run --deny-warnings --checked --json src/edit_cmdcomp_shell_test.lu > $o/hog$n.json 2> $o/hog$n.err
  echo "hog$n rc=$? secs=$(( $(date +%s) - s )) $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict"), "|", d.get("trap_message") or d.get("x-unsupported-construct") or "")' $o/hog$n.json 2>&1 | head -c 300)" >> $o/summary.txt
  kill $pids 2>/dev/null; wait 2>/dev/null
done
echo done >> $o/summary.txt
