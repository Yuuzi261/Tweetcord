# Contributing to Tweetcord

Thank you for your interest in contributing to Tweetcord! 🎉  
Whether you are fixing bugs, improving documentation, adding new features, or optimizing performance, your help is greatly appreciated.

Please take a moment to review this guide before submitting contributions.

---

## 🛠️ Prerequisites

- **Python**: `>= 3.11` (Python `3.12` is recommended and aligned with [.python-version](../.python-version)).
- **Git**: Installed and configured on your system.
- **Package Manager**:
  - [**uv**](https://docs.astral.sh/uv/) (Strongly recommended): Extremely fast Python package and project manager.
  - Or standard **pip** + **venv**.

---

## 🚀 Development Setup

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/Tweetcord.git
cd Tweetcord
```

Always branch off from the **`dev`** branch (see [Git Workflow](#-git-workflow--submitting-pull-requests)).

```bash
git checkout dev
git checkout -b feat/your-feature-name
```

### 2. Environment Setup

#### Option A: Using `uv` (Recommended)

`uv` automatically manages virtual environments and dependencies:

```bash
# Install both runtime dependencies and development tools (pytest, pytest-asyncio)
uv sync --all-groups
```

To run commands within the `uv` environment:
```bash
uv run python bot.py
uv run pytest
```

#### Option B: Using traditional `pip` and `venv`

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Local Configuration

1. Copy the example configuration:
   ```bash
   cp configs.example.yml configs.yml
   ```
2. Create your `.env` file with test credentials:
   ```env
   BOT_TOKEN=your_test_discord_bot_token
   TWITTER_TOKEN=TestAccount:your_twitter_auth_token
   DATA_PATH=./data
   ENABLE_FILE_LOGGING=true
   ```

---

## 📦 Dependency Management

Tweetcord supports both **`uv`** (PEP 517/621 + PEP 735) and traditional **`pip`**:

- **[`pyproject.toml`](../pyproject.toml) & [`uv.lock`](../uv.lock)**:
  - `[project.dependencies]`: Runtime dependencies.
  - `[dependency-groups.dev]`: Development and test dependencies (`pytest`, `pytest-asyncio`).
- **[`requirements.txt`](../requirements.txt) & [`requirements-dev.txt`](../requirements-dev.txt)**:
  - Kept in sync for users and environments that deploy using standard `pip`.

### Adding or Updating Dependencies

When adding or updating dependencies, please keep both systems synchronized:

1. **With `uv`**:
   ```bash
   # Add a runtime dependency
   uv add <package>

   # Add a development dependency
   uv add --dev <package>
   ```
2. **Update requirements files**:
   - If adding a runtime dependency, append it to [`requirements.txt`](../requirements.txt).
   - If adding a dev dependency, append it to [`requirements-dev.txt`](../requirements-dev.txt).

---

## 🧪 Testing Guidelines

We value high test coverage and hermetic tests to prevent regressions.

### Running Tests

```bash
# Run all tests using uv
uv run pytest

# Or using pytest in an activated virtual environment
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_log.py -v
```

### Writing Tests

- All tests are placed in the [`tests/`](../tests/) directory using standard `unittest` or `pytest`.
- **Test Isolation (Hermeticity)**:
  - Tests **must not** depend on personal `.env` credentials, live external APIs (Twitter, Discord), or local user configs.
  - Mock network calls, Discord API interactions, or filesystem operations where appropriate.
  - Reset any global state or caches (e.g. `LOG_BUFFER.clear()`) in `setUp()` / `tearDown()`.
- Whenever you add a new feature or fix a bug, please write corresponding tests in [`tests/`](../tests/).

---

## 🔀 Git Workflow & Submitting Pull Requests

### 1. Branching Strategy

- **`main`**: Production releases only.
- **`dev`**: Active development branch. **All PRs must target `dev`**.

### 2. Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature
- `fix:` A bug fix
- `perf:` Performance improvements
- `build:` Build system or dependency changes (`uv`, Dockerfile, pyproject.toml)
- `test:` Adding or updating tests
- `docs:` Documentation updates
- `refactor:` Code refactoring without changing behavior

Example:
```bash
git commit -m "feat: add optional file logging with in-memory ring buffer"
```

### 3. Pull Request Template & Checklist

When you open a Pull Request on GitHub, the [Pull Request Template](../.github/pull_request_template.md) will be loaded automatically. Please fill out the template and ensure:
- [ ] Code runs without warnings or errors.
- [ ] All tests pass: `pytest` or `uv run pytest`.
- [ ] New tests are added covering your changes.
- [ ] Documentation is updated in both:
  - [`docs/README.md`](./README.md) (English)
  - [`docs/README_zh.md`](./README_zh.md) (Traditional Chinese, AI translation can be used based on the README)
- [ ] PR targets the **`dev`** branch.

---

Thank you again for contributing to Tweetcord! 💙
