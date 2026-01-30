# Today's Task

**Note:** Ignore commented lines (surrounded by <!-- -->).

## Bug reported by user -->

we tried to run this command:

```python
from dataclasses import dataclass, field


@dataclass
class ExecuteServiceScript:
  """Executes a service script on its host."""

  executable: str = field(
    metadata={"help": "Relative path to executable script from root"},
  )
  script_args: list[str] = field(
    default_factory=list,
    metadata={"help": "Arguments to pass to the script"},
  )
  create_root: bool = field(
    default=False,
    metadata={"help": "Create remote root directory if it does not exist"},
  )

  def execute(self):
    from mhs.control.execute_service_script.handler import handle

    return handle(self)
```

.. and got an error:

```bash
scaf C:\\Users\\Dan\\Projects\\my-home-server --call=mhs/control/execute_service_script -- etc/ingress/init --skip-steps=00,10,11,20
usage: scaf C:/Users/Dan/Projects/my-home-server --call mhs/control/execute_service_script [-h] [--create-root] executable script_args
scaf C:/Users/Dan/Projects/my-home-server --call mhs/control/execute_service_script: error: the following arguments are required: script_args
✗  Invalid action arguments.
```

## Goals

- [ ] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file bugs/test_<%Y%m%d%H%M>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push
