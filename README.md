# Scaf

Scaf (straightforward composable application framework) is an opinionated filesystem-based scaffolding system for devs who just want to keep things simple.

Ask an agent to read the docs and the venvrc, then ask it to build what you need.

## Usage

Scaf can generate bash aliases for all action packages in a domain folder:

```bash
# Generate aliases for all actions in a domain
eval "$(scaf my-domain)"

# This creates aliases like:
# my-domain.action-name='scaf path/to/action'
# my-domain.deploy-remote-server='scaf path/to/deploy'
```

## Development

```bash
source dev/env.sh [--nuke]
```

**Note:** if you change packages or hooks, nuke your env.
