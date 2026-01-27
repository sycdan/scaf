ACTIVATE_SCRIPT=".venv/Scripts/activate"

if [[ "${1:-}" == "--nuke" ]]; then
  echo "💣 Nuking existing virtual environment..."
  rm -rf .venv
fi

if [ -d ".venv" ]; then
  if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "🪜  Activating existing virtual environment..."
    . "$ACTIVATE_SCRIPT"
  fi
  return
else
  deactivate > /dev/null 2>&1 || true
fi

echo "🪜  Creating virtual environment..."
python -m venv .venv || {
  echo "❌ Failed to create virtual environment"
  return 1
}

cat >> "$ACTIVATE_SCRIPT" <<'EOF'
# Source .venvrc, if it exists
if [ -f "$VIRTUAL_ENV/../.venvrc" ]; then
  . "$VIRTUAL_ENV/../.venvrc"
fi
EOF

echo "🪜  Activating virtual environment..."
. "$ACTIVATE_SCRIPT"

echo "🪜  Installing dev requirements..."
pip install -e .[dev] || {
  echo "Error: Failed to install packages"
  return 1
}

echo "🪜  Upgrading pip..."
python -m pip install --upgrade pip >/dev/null 2>&1

echo "🪜  Setting up git hooks..."
if [ -d ".git" ]; then
  mkdir -p .git/hooks >/dev/null 2>&1
  
  if [ -d "hooks" ]; then
    hook_count=0
    for hook_file in hooks/*; do
      if [ -f "$hook_file" ]; then
        hook_name=$(basename "$hook_file")
        rm -f ".git/hooks/$hook_name"
        cp "$hook_file" ".git/hooks/$hook_name" >/dev/null 2>&1
        chmod +x ".git/hooks/$hook_name"
        echo "✅ $hook_name hook installed"
        ((hook_count++))
      fi
    done
    
    if [ $hook_count -eq 0 ]; then
      echo "⚠️  No hooks found in hooks/ directory"
    else
      echo "📦 Installed $hook_count git hook(s)"
    fi
  else
    echo "⚠️  hooks/ directory not found"
  fi
else
  echo "⚠️  Not a git repository - skipping hook setup"
fi

echo "🪜  Generating aliases..."
eval "$(scaf scaf)"
alias | grep ' scaf.'

echo "🎉 Development environment ready!"
