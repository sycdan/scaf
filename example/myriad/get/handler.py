from example.myriad.entity import Myriad
from example.myriad.get.command import GetMyriad


def handle(command: GetMyriad):
  return Myriad()
