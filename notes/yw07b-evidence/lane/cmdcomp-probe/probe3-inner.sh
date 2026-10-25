set -u
o=$1
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
mount | grep ' /tmp ' > $o/tmp-mount.txt
for k in 1 2; do
  $W conform-run --deny-warnings --checked --json src/edit_cmdcomp_shell_test.lu > $o/tmpfs$k.json 2> $o/tmpfs$k.err
  echo "tmpfs$k rc=$? $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict"), "|", d.get("trap_message") or d.get("x-unsupported-construct") or "")' $o/tmpfs$k.json 2>&1 | head -c 400)" >> $o/summary.txt
done
echo done >> $o/summary.txt
