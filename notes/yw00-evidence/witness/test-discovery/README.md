G10 witness: `wolf test pkg` prints `pkg/a_test.lu::test_in_a` and
`pkg/z_test.lu::main` — two test files of the same shape, discovered two
ways, because `discover_tests` reads only the first file of the package
it builds for each test file (`lib.lu` sorts before `z_test.lu`, after
`a_test.lu`). Output recorded in `../run.txt`.
