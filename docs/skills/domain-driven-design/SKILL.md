---
name: domain-driven-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, action, model or service.
---
## Meaning of "Domain"

A domain is a conceptual boundary -- a slice of the system that represents a stable idea, not a specific instance or a collection of instances. Domains are named with **singular nouns** because they model concepts, not lists.

A **domain**...

- contains unversioned logic and entities
- evolves independently from API surfaces (which are versioned)
- provides action pathways for users to interact with domain objects

Think of a domain path like `organization.building.device.io` as a chain of nested concepts, each narrowing the scope of meaning. It's not describing "many organizations" or "many buildings" -- it's describing the conceptual space where each capability lives.

## Meaning of "Capability"

A **capability**...

- is a domain subsystem
- is a cohesive set of domain behaviors centered around a single domain concept
- comprises a set of operations (commands, queries)
- contains services that encapsulate domain logic
- evolves with the domain concept
- should not exist without at least one action
- is created automatically when the first action within it is created

**Example:**

```text
cyberdyne/           <- domain
  skynet/            <- domain
    defense/         <- capability
      fire_nukes/    <- action
        command.py   <- action shape
        handler.py   <- execution logic
```

### General rule for extracting capabilities from paths

Given a domain path like: `cyberdyne.skynet.offense.terminator.deploy`

Use this rule:

> Find the last noun before the verb

That noun (`terminator`) is the capability.

Everything before the verb comprises the domain.

## Meaning of "Action"

A domain **action**...

- represents something a capability can do at the request of a user
- applies the Single Responsibility Principle
- can be a query (read-only) or a command

By convention, a query can and should return cached data, but a command should not.

## Meaning of "Stable Entity"

A **stable entity**...

- exists in a domain
- has state
- may have an identifier
- does not expose its own actions
- is acted upon by a capability

**Example:**

```text
cyberdyne/             <- domain
  skynet/              <- domain
    defense/           <- capability
      nuke/            <- stable entity
        entity.py      <- entity shape
        rules.py       <- validation logic
      fire_nukes/      <- domain action
        command.py     <- action shape
        handler.py     <- execution logic
```

## Meaning of "Capable Entity"

A **capable entity**...

- exists in a domain
- has state
- has an identifier
- exposes one or more actions (typically simple verbs)

**Example:**

```text
cyberdyne/             <- domain
  skynet/              <- domain
    offense/           <- capability
      terminator/      <- capable entity
        entity.py      <- entity shape
        rules.py       <- validation logic
        commission/    <- action
          command.py   <- action shape
          handler.py   <- execution logic
        decommission/  <- action
          command.py   <- action shape
          handler.py   <- execution logic
        deploy/        <- action
          command.py   <- action shape
          handler.py   <- execution logic
        get/           <- action (returns entity state, read only)
          query.py     <- action shape
          handler.py   <- execution logic       
        set/           <- action (updates entity state)
          command.py   <- action shape
          handler.py   <- execution logic
```

**Example command.py:**

```python
@dataclass
class DeployTerminator:
  target_first: str = "Sarah"
  target_last: str = "Connor"
```

When using HTTP/1.1, commands must be invoked using the POST method.

**Example query.py:**

```python
@dataclass
class GetTerminator:
  health: int
  position: tuple[int]
```

When using HTTP/1.1, commands may be invoked using either POST or GET methods (POST is required for sufficiently large queries).

## Meaning of "Action Path"

The filesystem path to an action's files:

e.g. `cyberdyne/skynet/defense/fire_nukes`

The final segment of any action path is always the action to perform.

## FAQ

> "Where does validation logic live?"

```python
from example.<domain>.<capability>.<entity> import rules
```

> "Where is the shape of a read-only action defined?"

```python
from example.<domain>.<capability>.<verb_noun>.query import <VerbNoun>
```

> "Where is the shape of a read-write or write-only action defined?"

```python
# capable entity
from example.<domain>.<capability>.<noun>.<verb>.command import <VerbNoun>
# capability action
from example.<domain>.<capability>.<verb_noun>.command import <VerbNoun>
```

> "Where is an action's logic defined?"

```python
from example.<domain>.<capability>.<verb_noun>.handler import handle
```
