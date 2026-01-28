# Scaf

Scaf (straightforward composable application framework) is an opinionated filesystem-based scaffolding system for devs who just want to keep things simple.

## Setup

**Note:** Currently only bash is supported (use WSL or git bash on Windows).

Change to your project root:

```bash
cd ~/Projects/my-project
```

Create a venv:

```bash
python -m venv .venv
```

Add this to the end of your venv activate script (e.g. `.venv/Scripts/activate`):

```bash
if [ -f "$VIRTUAL_ENV/"../.venvrc ]; then
  source "$VIRTUAL_ENV/"../.venvrc
fi
```

Create a `.venvrc` file with content like content:

```bash
# Add project-specific aliases to the shell
eval "$(scaf .)"
alias | grep -P ' my-project(?=\.)'

# Add scaf's user aliases to the shell
eval "$(scaf)"
alias | grep -P ' scaf(?=\.)'
```

Install scaf:

```bash
.venv/Scripts/pip install git+http://github.com/sycdan/scaf
```

Activate the venv:

```bash
source .venv/Scripts/activate
```

Create an action:

```bash
scaf.create-action dev/do_stuff command
```

Add the new action alias and call it:

```bash
eval "$(scaf .)"
my-project.do-stuff
```

## Usage

Ask an agent to build or do what you need using the available aliases.

## Development

```bash
source dev/env.sh [--nuke]
```

**Note:** If you change packages or hooks, nuke your env.

## F.A.Q

- But `eval` is **evil**!
  - That's not a question.
- I tried to run `xyz.foo` and got `ModuleNotFoundError: No module named 'xyz'`, help!
  - Also not a question, but try this:
    - `export PYTHONPATH=.`
    - `xyz.foo`
