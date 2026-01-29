# action_path, expected_alias
actions_to_create = [
  ("init", "test0.init"),  # Simple action at root
  ("deploy", "test0.deploy"),  # Another root level action
  ("auth/login", "test0.login"),  # Nested action with clear hierarchy
  ("auth/logout", "test0.logout"),  # Another action in same namespace
  ("api/user/create", "test0.create-user"),  # Deeply nested action
  ("api/post/create", "test0.create-post"),  # Conflict resolved by parent
]


def test(sandbox):
  aliases = sandbox.get_aliases()
  create_action = next((a for a in aliases if a.name == "scaf.create-action"), None)
  assert create_action is not None
  for action_path, expected_alias in actions_to_create:
    result = sandbox.run_scaf(create_action.scaf_args + f" {action_path} command")
    assert result.returncode == 0
    assert sandbox.exists(action_path)
  aliases = sandbox.get_aliases(".")
  assert len(aliases) == len(actions_to_create)
