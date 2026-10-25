set -u
echo "tree rev=706933b18ac265658688716f6989c585053edb8c"
head -1 /etc/os-release; dpkg-query -W libc6; uname -m
tools/fetch-toolchain || exit 3
.wolf-bin/wolf --version | head -1
tools/build --static; echo BUILD rc=$?
f=target/static/yew
[ -f $f ] || exit 4
readelf -h $f | grep -E "Type:|Machine:"
echo PT_INTERP=$(readelf -l $f | grep -c INTERP)
file $f
$f --version; echo VERSION rc=$?
$f fl -e 'io.print("hello, world")'; echo FL_E rc=$?
sha256sum $f; sha256sum $f; stat -c "bytes %s" $f
