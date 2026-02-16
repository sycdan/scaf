from example.pass_dynamic_args.command import PassDynamicArgs


def handle(command: PassDynamicArgs, *args):
  return command.Result(extra_args=list(args))
