from dataclasses import dataclass, field
from uuid import UUID

from scaf.core import Shape


@dataclass
class Entity:
  guid: UUID


@dataclass
class EntityRef(Shape):
  key: str
  guid: UUID = field(init=False)

  def prepare(self):
    self.guid = UUID(self.key[7:])

  def hydrate(self) -> Entity:
    return Entity(guid=self.guid)
