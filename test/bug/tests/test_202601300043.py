"""Bug test: script_args with default_factory should not be required."""


def test_script_args_with_default_factory_not_required(sandbox):
  """
  Bug: When a dataclass field has default_factory=list,
  scaf incorrectly treats it as required and throws:
  "error: the following arguments are required: <field_name>"

  Expected: The field should be optional since it has a default.
  """
  # Create command.py with the problematic field structure
  sandbox.write("test_service/execute_script/__init__.py", "")
  sandbox.write(
    "test_service/execute_script/command.py",
    '''from dataclasses import dataclass, field


@dataclass
class ExecuteScript:
  """Executes a service script on its host."""

  executable: str
  script_args: list[str] = field(
    default_factory=list,
    metadata={"help": "Arguments to pass to the script"},
  )
''',
  )

  # Create handler.py
  sandbox.write(
    "test_service/execute_script/handler.py",
    """from test_service.execute_script.command import ExecuteScript


def handle(command: ExecuteScript):
  return {
    "executable": command.executable,
    "script_args": command.script_args,
  }
""",
  )

  # Try to call the action with only the required executable argument
  # This should work since script_args has default_factory=list
  result = sandbox.run(
    "scaf",
    ".",
    "--call=test_service/execute_script",
    "--",
    "init",  # Only providing executable, not script_args
  )

  assert result.returncode == 0, (
    f"Command failed with return code {result.returncode}.\n"
    f"stdout: {result.stdout}\n"
    f"stderr: {result.stderr}\n"
    "script_args with default_factory=list should be optional"
  )

  # Should not contain error message about script_args being required
  assert "error: the following arguments are required: script_args" not in result.stderr, (
    f"script_args should be optional due to default_factory. stderr: {result.stderr}"
  )
