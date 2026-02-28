# Scaf

**_Build more, sweat less._**

Scaf is an opinionated filesystem-based project builder and domain-action runner for devs who just want to keep things simple. It solves the easy problems in application development, so you can focus on the hard ones.

## Usage

**Note:** Currently only bash is supported (use WSL or git bash on Windows).

Install scaf (can be in your user/system env, but a [`venv`](#what-is-a-venv) is recommended):

```bash
pip install git+http://scaf.sycdan.com
```

Initialize scaf in your project root:

```bash
scaf init
```

Add this to your [`.venvrc`](#what-is-venvrc) or `.bashrc` file:

```bash
scaf discover . && source .scaf/aliases
```

Invoke an action (this will create it and add an alias, if it does not exist):

```bash
scaf call example/world/greet
```

## Dev Server

Start the local dev server to run and test your domain actions from a browser UI:

```bash
scaf serve .
```

Then open [http://localhost:54545](http://localhost:54545).

Select an action, enter a JSON payload, choose which tests to run and whether you expect each to pass or fail, then hit **Submit**. The server saves the payload as a fixture in the action's `fixtures/` folder and runs the selected tests in-process, returning live results. The server also hot-reloads any `.py` files under the deck as you edit them — no restart needed.

Additionally, you can launch the server with debugpy via VSCode's `launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug dev server",
      "type": "debugpy",
      "request": "launch",
      "module": "scaf",
      "args": [
        "-vvv",
        "serve",
        "."
      ]
    }
  ]
}
```

## Development

Keep dependencies to a minimum.

Use **2-space indentation** in all Python files. Scaf's generated templates use 2-space indent, so consistency matters.

### Environment Setup

```bash
source dev/env.sh [--nuke]
```

**Note:** If you change packages or hooks, nuke your env.

## FAQ

### How do I see verbose output from scaf calls?

Edit your `.scaf/aliases` file:

```bash
alias domain.action="scaf --vvv call $DECK/domain/action"
#                         ^ add this
```

### Why am I getting `Failed to load action package backend/domain/action: No module named 'domain'`

Run `scaf init` in your app's `PYTHONPATH` directory (e.g. `backend`).

### Why am I getting `MyType | None is not callable`?

You are probably on an old python version -- use `Union[MyType, None]` instead.

### What is a `venv`?

A python virtual environment, allowing you to have project-specific dependencies.
Create one thus:

```bash
python -m venv .venv
```

### What is `.venvrc`?

A file intended to be sourced when your venv is activated. Typically placed in your project root.

Add this to the end of your venv activate script (e.g. `.venv/Scripts/activate`):

```bash
if [ -f "$VIRTUAL_ENV/"../.venvrc ]; then
  source "$VIRTUAL_ENV/"../.venvrc
fi
```
