# Today's Task

**Note:** Ignore commented lines (surrounded by <!-- -->).


We need to add functionality tot he cli. if the provided work folder is not an action package, assume it's a domain/capability and walk the tree, looking for valid action packages within.

when all are found, we will output (to stdout, so all other output should go to stderr) a list of aliases in bash syntax, so the user can source it in their shell to make commands available.

the aliases should be named <work_folder_name>.<action-name>. if there are deplicates, deduplicate by adding the name of the parent folder of the action, and continue doing so as necessary

e.g.

mhs/control/deploy_device -> mhs.deploy-device
mhs/fleet/load -> mhs.load-fleet
mhs/server/load -> mhs.load-server


<!-- ## Bug reported by the client -->
<!-- ## Goals

- [ ] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file test_bug_<timestamp>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push -->