f=target/static/yew
$f fl -e 'import io; io.print("hello, world")'; echo FL_E rc=$?
printf 'import io\nio.print("hello, world")\n' > $HOME/hello.fl
$f fl $HOME/hello.fl; echo FL_FILE rc=$?
sha256sum $f; sha256sum $f; stat -c "bytes %s" $f
