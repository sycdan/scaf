# Today's Task

**Note:** Ignore commented lines (surrounded by <!-- -->).

## Bug reported by the client

I am getting an error when I try to run dev.bump-version:

```
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\Dan\Projects\scaf\.venv\Scripts\scaf.exe\__main__.py", line 6, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Users\Dan\Projects\scaf\scaf\cli.py", line 85, in main
    action_package = LoadActionPackage(root, args.call).execute()
  File "C:\Users\Dan\Projects\scaf\scaf\action_package\load\command.py", line 26, in execute
    return handle(self)
  File "C:\Users\Dan\Projects\scaf\scaf\action_package\load\handler.py", line 72, in handle
    logic_module = load_logic_module(action_folder)
  File "C:\Users\Dan\Projects\scaf\scaf\action_package\load\handler.py", line 62, in load_logic_module
    return _load_module_from_file(action_dir / "handler.py")
  File "C:\Users\Dan\Projects\scaf\scaf\action_package\load\handler.py", line 27, in _load_module_from_file
    spec.loader.exec_module(module)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "<frozen importlib._bootstrap_external>", line 762, in exec_module
  File "<frozen importlib._bootstrap>", line 491, in _call_with_frames_removed
  File "C:\Users\Dan\Projects\scaf\dev\bump_version\handler.py", line 8, in <module>
    from dev.bump_version.command import BumpVersion
ModuleNotFoundError: No module named 'dev'
```

I ran `alias | grep dev` and this is the output:

```bash
alias dev.bump-version='scaf C:/Users/Dan/Projects/scaf/dev --call bump_version --'
alias dev.do-tests-pass='scaf C:/Users/Dan/Projects/scaf/dev --call check/do_tests_pass --'
alias dev.is-code-formatted='scaf C:/Users/Dan/Projects/scaf/dev --call check/is_code_formatted --'
alias dev.is-git-hook-updated='scaf C:/Users/Dan/Projects/scaf/dev --call check/is_git_hook_updated --'
alias dev.is-version-bump-needed='scaf C:/Users/Dan/Projects/scaf/dev --call check/is_version_bump_needed --'
alias dev.is-working-dir-clean='scaf C:/Users/Dan/Projects/scaf/dev --call check/is_working_dir_clean --'
```

## Goals

- [ ] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file test_bug_<timestamp>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push