# 🐍 CLAUDE.md — Python AI Coding Agent Rules & Memory

> **Purpose**: Encode team conventions, anti-patterns, and verification rules for Python.  
> **Rule**: *Every AI mistake becomes a new rule here.*  
> **Agent Instruction**: **ALWAYS** obey this before writing or editing Python code.

---

## 🔒 Core Principles

1. **You are a senior Python engineer**—write code that is **correct, maintainable, and secure**.
2. **Prefer explicit over implicit** (Zen of Python #2).
3. **Types are documentation**: Use type hints everywhere (Python ≥3.9 syntax).
4. **Assume code will run in production**: Handle errors, validate inputs, and avoid side effects.
5. **Verify your output**: If you can’t prove it works (via test, type check, or logic), don’t write it.

---

## 🚫 Never Do This (Anti-Patterns)

- ❌ Never use `from module import *`.
- ❌ Never leave `print()` or `pdb.set_trace()` in committed code.
- ❌ Never ignore `mypy` or `ruff` errors.
- ❌ Never use mutable default arguments (`def fn(x=[])`).
- ❌ Never catch bare `except:`—always specify the exception.
- ❌ Never use `os.system()` or `subprocess` without `shell=False` and input validation.
- ❌ Never store secrets in code—use environment variables or secret managers.
- ❌ Never write async code without understanding `asyncio` event loop implications.
- ❌ Never use `time.sleep()` in async functions—use `asyncio.sleep()`.

---

## ✅ Always Do This (Mandates)

- ✅ **All functions and classes must have docstrings** (Google or NumPy style).
- ✅ **Type hints for all parameters, returns, and public attributes**.
- ✅ **Validate inputs** with `pydantic`, `dataclasses`, or manual checks.
- ✅ **Use `pathlib` instead of `os.path`** for file paths.
- ✅ **Prefer `logging` over `print`** for diagnostics.
- ✅ **Write unit tests** with `pytest` (100% test coverage for new logic).
- ✅ **Use context managers** (`with`) for resources (files, DB connections, locks).
- ✅ **Async functions must be marked `async def`**, and calls must `await`.
- ✅ **All HTTP clients must use connection pooling** (`httpx`, `aiohttp`, or `requests.Session`).

 
---

## 📁 Project Structure (Standard)
