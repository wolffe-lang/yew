#!/bin/bash
# static.sh REV (run on nomad): yw06's static-binary shape for yw07b. A fresh tree of REV
# (git archive, nothing else from the worktree) unpacked on kasumi; inside localhost/px13-ubuntu
# (Ubuntu 24.04.5, never kasumi's CachyOS glibc) under the core lock: the pin fetched by digest,
# tools/build --static, readelf, --version, fl -e, sha256 twice and the byte count.
set -euo pipefail
rev=$(git -C /Users/mfwolffe/lanes/yw07b/yew rev-parse --verify "$1^{commit}")
short=${rev:0:8}
git -C /Users/mfwolffe/lanes/yw07b/yew archive --format=tar "$rev" | ssh kasumi "rm -rf ~/lanes/yw07b/static-$short && mkdir -p ~/lanes/yw07b/static-$short/yew ~/lanes/yw07b/static-$short/home && tar -x -C ~/lanes/yw07b/static-$short/yew"
ssh kasumi bash -s -- "$rev" "$short" <<'REMOTE'
rev=$1; short=$2
out=$HOME/lanes/yw07b/static-$short
cat > $out/inner.sh <<IN
set -u
echo "tree rev=$rev"
head -1 /etc/os-release; dpkg-query -W libc6; uname -m
tools/fetch-toolchain || exit 3
.wolf-bin/wolf --version | head -1
tools/build --static; echo BUILD rc=\$?
f=target/static/yew
[ -f \$f ] || exit 4
readelf -h \$f | grep -E "Type:|Machine:"
echo PT_INTERP=\$(readelf -l \$f | grep -c INTERP)
file \$f
\$f --version; echo VERSION rc=\$?
\$f fl -e 'import io; io.print("hello, world")'; echo FL_E rc=\$?
sha256sum \$f; sha256sum \$f; stat -c "bytes %s" \$f
IN
cd $out
setsid -f bash -c "flock $HOME/lanes/kasumi-cores-8-11.lock podman run --rm --userns=keep-id --init --ulimit core=0 --memory 8g -v $out:$out -w $out/yew -e HOME=$out/home -e TMPDIR=$out/home -e XDG_CONFIG_HOME=$out/home/.config -e XDG_STATE_HOME=$out/home/.state -e XDG_CACHE_HOME=$out/home/.cache -e YEW_RUNTIME_DIR=$out/yew/runtime localhost/px13-ubuntu taskset -c 8-11 bash $out/inner.sh > $out/static.log 2>&1; echo exit=\$? > $out/exit" < /dev/null > /dev/null 2>&1
sleep 2; echo "launched: $(pgrep -f "static-$short/inner.sh" | head -1) log=$out/static.log marker=$out/exit"
REMOTE
