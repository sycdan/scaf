from dataclasses import dataclass

from example.custom_union_types.entity import Entity, EntityRef


@dataclass
class TestCustomUnionTypes:
  entity: Entity | EntityRef | None
  """Take the least-specific non-null type in the union (EntityRef)."""

  @dataclass
  class Result:
    type_name: str
    entity: object
