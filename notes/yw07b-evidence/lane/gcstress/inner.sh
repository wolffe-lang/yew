set -u
o=$1; n=$2
c=target/oracle/sagitta/build/yew; p=target/release/yew
: > $o/samples.tsv
for i in $(seq 1 $n); do
  for who in c port; do
    b=$c; [ $who = port ] && b=$p
    s=$(date +%s%N)
    YEW_FL_GC_STRESS=1 tools/goldens --yew $b --suite fletch > $o/$who-$i.log 2>&1
    rc=$?
    e=$(date +%s%N)
    echo "$who $i $rc $(( (e - s) / 1000 )) $(grep -c '^PASS ' target/oracle/goldens/fletch.log)" >> $o/samples.tsv
  done
done
python3 -I - $o/samples.tsv > $o/summary.txt <<'PY'
import sys, statistics
rows=[l.split() for l in open(sys.argv[1])]
med={}
for who in ("c","port"):
    us=[int(r[3]) for r in rows if r[0]==who]
    rc=set(r[2] for r in rows if r[0]==who); passes=set(r[4] for r in rows if r[0]==who)
    med[who]=statistics.median(us)
    print("%s n=%d exits=%s pass=%s median_us=%d min_us=%d" % (who, len(us), ",".join(sorted(rc)), ",".join(sorted(passes)), med[who], min(us)))
print("ratio wolf/C (median) = %.3f" % (med["port"]/med["c"]))
PY
echo done >> $o/summary.txt
