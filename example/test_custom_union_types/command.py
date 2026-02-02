from dataclasses import dataclass

from example.test_custom_union_types.entity import Entity, EntityRef


@dataclass
class TestCustomUnionTypes:
  entity: Entity | EntityRef | None
  """We'll take the least-specific non-null type in the union (EntityRef)."""
