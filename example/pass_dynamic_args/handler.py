from example.pass_dynamic_args.command import PassDynamicArgs


def handle(command: PassDynamicArgs, *args):
  return {"executable": command.executable, "args": args}
