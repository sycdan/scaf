from example.pass_dynamic_args.command import PassDynamicArgs


def handle(command: PassDynamicArgs, *args, **kwargs):
  return f"{command.executable} {' '.join(args)}"
