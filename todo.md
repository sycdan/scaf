# Today's Task

**Note:** Ignore commented blocks (surrounded by <!-- -->).

## Bug reported by user

I am trying to pass variable arguments to a command, which i want to then pass on to another script, but i get an error:

```bash
scaf . --call example/pass_dynamic_args/ -- init --with-flag
usage: scaf C:/Users/Dan/Projects/scaf --call example/pass_dynamic_args [-h] executable
scaf C:/Users/Dan/Projects/scaf --call example/pass_dynamic_args: error: unrecognized arguments: --with-flag
✗  Invalid action arguments.
```

## Goals

- [x] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file bug/tests/test_<%Y%m%d%H%M>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push
