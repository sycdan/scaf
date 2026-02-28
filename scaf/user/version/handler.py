import scaf

from scaf.user.version.query import Version


def handle(command: Version):
  print(scaf.__version__)
