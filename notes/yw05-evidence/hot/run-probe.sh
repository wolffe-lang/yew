#!/bin/bash
# yw05-hot: the in-process probe (hotprobe.lu) on both tiers, inside the
# container from the tree root. run-probe.sh TAG [PHASE] [ROOT] [SRC] ->
# target/hot/probe-TAG.txt. ROOT (default: the tree) is the source tree the
# probe is built against and run in (a git worktree at the baseline under
# target/hot/ measures the baseline with this probe). The probe is copied
# into ROOT/src for the build (a `use edit` resolves beside the entry file,
# D32) and removed after; SRC (default README.md, relative to ROOT) is the
# file it opens. TIERS (default "native release") picks the tiers; PROBE
# (default notes/yw05-evidence/hot/hotprobe.lu) the probe's source.
set -u
tag=$1; ph=${2:-all}; root=${3:-.}; src=${4:-README.md}
top=$PWD; h=$top/notes/yw05-evidence/hot; w=$top/.wolf-bin/wolf
probe=${PROBE:-$h/hotprobe.lu}
out=$top/target/hot/probe-$tag.txt; mkdir -p $top/target/hot
cp $probe $root/src/zzhot_probe.lu
cd $root; mkdir -p target/verify
{
echo "# $(basename $probe) ($(sha256sum $probe | cut -c1-12)), tag $tag, phase $ph, root $root at $(git rev-parse --short HEAD) (src diff: $(git diff --stat HEAD -- src | tail -1)), $(date -u +%FT%TZ), cpus $(taskset -pc $$ | sed 's/.*: //')"
for tier in ${TIERS:-native release}; do
  fl=""; [ $tier = release ] && fl=--release
  if $w build $fl src/zzhot_probe.lu -o $top/target/hot/zzhot-$tag-$tier > $top/target/hot/zzhot-build-$tag-$tier.log 2>&1; then
    rm -rf "$XDG_STATE_HOME/yew"
    echo "## $tier $(sha256sum $top/target/hot/zzhot-$tag-$tier | cut -c1-12)"
    $top/target/hot/zzhot-$tag-$tier $ph $src 2>&1
    echo "## $tier rc=$?"
  else
    echo "## $tier BUILD FAILED"; tail -40 $top/target/hot/zzhot-build-$tag-$tier.log
  fi
done
} > $out 2>&1
rm -f src/zzhot_probe.lu
