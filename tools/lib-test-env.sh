# lib-test-env.sh — private HOME/XDG roots for programs the harness runs.
# C fixtures do this themselves (sagitta tests/unit/test_ws_key.c:29-85),
# but not every C test/runner does. yew#11: never lend the caller's state
# home to either editor. Call after oracle fetch (git may need credentials)
# and before building/running test programs. These two harnesses own EXIT.
test_env_begin() {
    : "${YEW_ROOT:?test_env_begin needs YEW_ROOT}"
    mkdir -p "$YEW_ROOT/target"
    YEW_TEST_ENV=$(mktemp -d "$YEW_ROOT/target/test-home.XXXXXX") || return 1
    trap 'rm -rf -- "$YEW_TEST_ENV"' EXIT
    export HOME="$YEW_TEST_ENV/home" XDG_STATE_HOME="$YEW_TEST_ENV/state"
    export XDG_CONFIG_HOME="$YEW_TEST_ENV/config" XDG_CACHE_HOME="$YEW_TEST_ENV/cache"
    mkdir -p "$HOME" "$XDG_STATE_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" || return 1
}
