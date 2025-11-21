# VP Track Status

Victoria Park Track Status - predicting track running conditions based on rainfall data.

## Development Setup

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Install lefthook Git hooks
lefthook install
```

## Pre-commit Hooks

This project uses [lefthook](https://github.com/evilmartians/lefthook) to run pre-commit hooks. The hooks automatically run when you commit changes:

- **ruff check**: Lints staged Python files
- **ruff format**: Formats staged Python files

Both commands run in parallel and automatically stage any fixes.

### Installing lefthook

If you don't have lefthook installed:

```bash
# macOS
brew install lefthook
```

After installing, run `lefthook install` in the project directory.

To run hooks manually:

```bash
lefthook run pre-commit
```
