---
applyTo: "**/*.proto"
---

# Protobuf Standards (must be followed exactly)

## Schema Mutability

- Adding new fields is always safe.
- Changing wiretypes on fields is breaking.
- Never reuse field numbers (critical).
- Reserve deleted field numbers (recommended).

## Coding Style

- Use 2 spaces for indentation, no tabs.
- Limit lines to a maximum of 99 characters.

## Additional Rules

- Use `edition = "2024"` in all `.proto` files.
  - [More info](https://protobuf.dev/programming-guides/editions/#edition-2024)
- Use a `package` path that reflects the domain structure and directory layout:
  - Example: `proto/tld/do_stuff/v1/contract.proto` `package tld.do_stuff.v1;`
