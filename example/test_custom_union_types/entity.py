from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class Entity:
  guid: UUID


@dataclass
class EntityRef:
  key: str
  guid: UUID = field(init=False)

  def __post_init__(self):
    self.guid = UUID(self.key[7:])

  def hydrate(self) -> Entity:
    return Entity(guid=self.guid)
