Zen Programming Language

<div align="center">
  <p><strong>Simple to write. Clear to understand. Controlled to execute.</strong></p><a href="https://github.com/zixzax141298-ui/Zen/actions"><img src="https://github.com/zixzax141298-ui/Zen/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
<img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="Python Versions">
<img src="https://img.shields.io/badge/status-v0.1.0--prototype-orange" alt="Status">

</div>---

What is Zen?

Zen is a general-purpose, dynamically typed, interpreted programming language designed around readable syntax, explicit structure, and controlled execution.

ZEN is being developed incrementally, with an emphasis on correctness, architectural boundaries, validation, and independently verifiable engineering evidence.

Key Features

- Lexer and Parser: Tokenization and recursive-descent parsing for ZEN source code.
- Semantic Analysis: Strict semantic validation before execution through the CLI validation workflow.
- AST Validation: Structural validation of parsed Abstract Syntax Trees.
- Tree-Walk Interpreter: Execution of validated programs with runtime resource guardrails.
- Command-Line Interface: Run, validate, inspect, format, and fingerprint ".zen" source files.
- Interactive REPL: Persistent interactive sessions, multiline input, variable inspection, save/load commands, and rollback of global state after failed runtime submissions.
- ZIIF (ZEN AST Identity Fingerprint): A SHA-256-based fingerprint derived from a canonicalized AST representation.
- Shell Completion: Bash and Zsh completion generation, installation, and uninstallation.

---

Quick Start

ZEN requires Python 3.10 or newer. The package currently declares no third-party runtime dependencies.

Installation

git clone https://github.com/zixzax141298-ui/Zen.git
cd Zen
python -m pip install -e .

Run a program

Create "hello.zen":

let first = 20
let second = 22
first + second

Execute it:

zen run hello.zen

Expected result:

42

---

CLI Toolchain

ZEN provides commands for common development tasks.

Command| Purpose
"zen run file.zen"| Validate and execute a source file
"zen check file.zen"| Validate without executing
"zen ast file.zen"| Display the AST as JSON
"zen tokens file.zen"| Display the token stream
"zen format file.zen"| Validate and print normalized outer whitespace
"zen fp file.zen"| Generate the ZIIF fingerprint
"zen repl"| Start the interactive shell
"zen docs"| Display a quick language reference
"zen env"| Display environment information
"zen version"| Display the ZEN version
"zen doctor"| Inspect basic CLI and Python environment details

"zen fmt" is also available as an alias for "zen format".

Additional CLI options

# Machine-readable validation output
zen check hello.zen --json

# Machine-readable execution output and timing statistics
zen run hello.zen --json --stats

# Set an execution timeout
zen run hello.zen --timeout 5

Shell completion

ZEN supports Bash and Zsh completion.

# Install Bash completion
zen completion bash --install

# Remove ZEN-managed Bash completion
zen completion bash --uninstall

# Install Zsh completion
zen completion zsh --install

# Remove ZEN-managed Zsh completion
zen completion zsh --uninstall

---

Interactive REPL

Start an interactive session:

zen repl

Example:

>>> let x = 40
>>> let y = 2
>>> x + y
42
>>> :vars
  let x = 40
  let y = 2
>>> :save session.zen
Saved ... chars to session.zen.

Available commands:

Command| Purpose
":help"| Show REPL help
":vars"| List global variables
":ast"| Show a summary of the current session AST
":save <file>"| Save session source to a file
":load <file>"| Load and execute a ".zen" file into the session
":reset"| Clear the current session
":quit"| Exit the REPL

The REPL supports multiline input and retains variables between successful submissions. Failed runtime submissions restore the session's global variable and constant mappings.

---

ZIIF: ZEN AST Identity Fingerprint

ZIIF generates a fingerprint from a canonicalized representation of a parsed AST.

The current implementation:

- Canonicalizes AST structures into JSON.
- Excludes source-location metadata such as "span" and "source_id".
- Sorts JSON object keys for deterministic serialization.
- Uses SHA-256 and displays the first 32 hexadecimal characters with the "z1-" prefix.

Example:

from zen import parse
from zen.ziif import generate_fingerprint

source = "let answer = 40 + 2"

program = parse(source)
fingerprint = generate_fingerprint(program)

print(fingerprint)

The fingerprint can help compare AST structures and detect changes in the canonicalized representation.

Security boundary: ZIIF is an AST fingerprinting mechanism. By itself, it is not a digital signature, does not authenticate the author or review process, and does not prove that a particular runtime execution used the reviewed source. Those stronger guarantees require additional mechanisms and verification.

---

Python API

ZEN can also be used from Python applications.

High-level execution

from zen import execute

result = execute("""
fn add_one(value) {
    return value + 1
}

add_one(41)
""")

print(result)  # 42

Parsing and analysis

from zen import parse, analyze, interpret

program = parse("1 + 2 * 3")
analyze(program)

result = interpret(program)
print(result)  # 7

---

Development and Testing

Install the package and test runner:

python -m pip install -e .
python -m pip install pytest

Run the test suite:

python -m compileall -q src tests
python -m pytest -q

The GitHub Actions CI workflow tests Python 3.10, 3.11, 3.12, 3.13, and 3.14.

Test counts can change as the project evolves. Refer to the current CI run for the verified result rather than relying on a fixed number in this README.

---

Project Structure

src/zen/
├── cli.py
├── cli_core/
├── cli_commands/
├── lexer.py
├── parser.py
├── semantic/
├── runtime/
├── sandbox/
└── ziif.py

The project separates language front-end processing, semantic validation, runtime execution, CLI orchestration, and supporting components.

---

Documentation

- "Language Specification" (docs/03-language-specification.md)
- "Installation Guide" (docs/02-installation.md)
- "Changelog" (CHANGELOG.md)

---

<div align="center">
  <i>Small steps. Clear purpose. Evidence before claims.</i>
</div>
