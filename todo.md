# Today's Task

**Note:** Ignore commented lines (surrounded by <!-- -->).

calling scaf with no args currently outputs this

```bash
> scaf
alias scaf.user.create-action='scaf C:/Users/Dan/Projects/scaf --call scaf/user/create_action --'
alias scaf.user.get-version='scaf C:/Users/Dan/Projects/scaf --call scaf/user/get_version --'
```

but we want it to output

```bash
alias scaf.create-action='scaf C:/Users/Dan/Projects/scaf --call scaf/user/create_action --'
alias scaf.get-version='scaf C:/Users/Dan/Projects/scaf --call scaf/user/get_version --'
```

the capability (user in this case) should only be added to the path if necessary for deduplication.

<!-- ## Goals

- [ ] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file test_bug_<timestamp>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push -->