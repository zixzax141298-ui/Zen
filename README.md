<div align="center">
  <h1>Zen Programming Language</h1>
  <p><strong>Simple to write. Clear to understand. Cryptographically verifiable to execute.</strong></p>

  <!-- Badges -->
  <a href="https://github.com/zixzax141298-ui/Zen/actions"><img src="https://github.com/zixzax141298-ui/Zen/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="Python Versions">
  <img src="https://img.shields.io/badge/tests-339%20passed-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/status-v0.1.0--prototype-orange" alt="Status">
</div>

---

## 📖 What is Zen?

Zen is a general-purpose, dynamically typed, and interpreted programming language designed for clarity and absolute execution control. 

While most languages only guarantee safety *inside* their runtime, Zen goes a step further by providing **Cryptographic Execution Identity**. With Zen, you can prove that the code being executed is exactly the code you reviewed, down to the semantic structure.

### ✨ Key Features

- **ZIIF (Zen AST Identity Fingerprint)**: Every program has a unique, canonical SHA-256 fingerprint based on its Abstract Syntax Tree (AST). Whitespace and comments do not change the fingerprint, but any semantic change will.
- **Complete CLI Toolchain**: Run, check, inspect, format, and fingerprint code directly from the terminal.
- **Fail-Closed Security**: Strict semantic analysis, AST validation, and runtime resource limits (timeouts, recursion depth) prevent catastrophic execution.
- **Powerful REPL**: An interactive shell with state management (`:save`, `:load`, `:vars`) and automatic rollback on errors.

---

## 🚀 Quick Start

Zen requires **Python 3.10+** and has zero third-party runtime dependencies.

### 1. Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/zixzax141298-ui/Zen.git
cd Zen
pip install -e .
```

### 2. The CLI Toolchain

Zen comes with a fully featured Command-Line Interface.

```bash
# Run a Zen file
zen run script.zen

# Check syntax and semantics without executing
zen check script.zen

# Print the ZIIF (Fingerprint) of a file
zen fp script.zen
# Output: z1-539d9d16c3210517a4b401bd1fdc024f

# Inspect tokens and AST
zen tokens script.zen
zen ast script.zen

# Start the interactive REPL
zen repl
```

### 3. The Interactive REPL

The Zen REPL is designed for rapid prototyping and safe exploration:

```text
>>> let x = 40
>>> let y = 2
>>> x + y
42
>>> :vars
  let x = 40
  let y = 2
>>> :save session.zen
Saved 18 chars to session.zen.
```

*(Type `:help` inside the REPL to see all available commands).*

---

## 🧬 ZIIF: AST Identity Fingerprint

ZIIF is Zen's flagship security feature. Because it hashes the **canonical AST** instead of raw text, you can verify the integrity of Zen code in untrusted environments.

```python
from zen import execute, parse
from zen.ziif import generate_fingerprint

# Two syntactically different but semantically identical programs
code_a = "let x = 40 + 2"
code_b = "    let x = 40 + 2   \n\n"

fp_a = generate_fingerprint(parse(code_a))
fp_b = generate_fingerprint(parse(code_b))

print(fp_a == fp_b) # True (Fingerprints match!)
```

If a malicious actor tries to inject logic (e.g., changing `let x` to `let hack`), the fingerprint changes immediately, allowing CI pipelines to block the execution.

---

## 🐍 Python API

You can embed Zen directly into your Python applications.

### Safe High-Level API
```python
from zen import execute

# Parses, validates semantics strictly, and runs in a fail-closed environment
result = execute("fn f(x) { return x + 1 }\nf(41)")
print(result) # 42
```

### Low-Level API
```python
from zen import parse, analyze, interpret

program = parse("1 + 2 * 3")
analyze(program) # Semantic check
result = interpret(program)
print(result) # 7
```

---

## 🛠️ Development & Testing

Zen is built with a strict test-driven development approach, ensuring stability across multiple Python versions.

To run the test suite (includes CLI integration, sandbox, and ZIIF tests):

```bash
python -m pytest -q
# Output: 339 passed, 110 subtests passed
```

### Project Structure
```text
src/zen/
├── cli.py       # Complete CLI toolchain & REPL
├── lexer.py     # Tokenization
├── parser.py    # Recursive-descent parser
├── semantic/    # Semantic analysis & validation
├── runtime/     # Tree-walk interpreter
├── sandbox/     # Resource boundaries & policies
└── ziif.py      # AST Identity Fingerprint
```

---

## 📄 Documentation

- [Language Specification](docs/03-language-specification.md)
- [Installation Guide](docs/02-installation.md)
- [Changelog](CHANGELOG.md)

---
<div align="center">
  <i>Built with discipline, strict rules, and a passion for secure languages.</i>
</div>
