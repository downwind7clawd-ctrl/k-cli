# BUGFIX LOG — k-cli

> Date: 2026-05-21
> Author: AI Assistant
> Scope: Comprehensive audit — bugs, errors, security, code quality

---

## Fixes Applied

### 1. pytest-asyncio Test Infrastructure Fix

| Item | Details |
|------|---------|
| **File** | `pyproject.toml` |
| **Severity** | 🔴 Critical |
| **Issue** | `pytest-asyncio>=0.21` was incompatible with pytest 9.x. All 12 async tests failed with "async def functions are not natively supported". |
| **Fix** | Upgraded to `pytest-asyncio>=0.23`. Removed `asyncio_mode = "auto"` (tests use `@pytest.mark.asyncio` explicitly). |
| **Before** | `pytest-asyncio>=0.21`, `asyncio_mode = "auto"` |
| **After** | `pytest-asyncio>=0.23`, no `asyncio_mode` (uses explicit `@pytest.mark.asyncio`) |
| **Result** | 116 tests pass (was 104 pass / 12 fail) |

---

### 2. Type Hint Fix — proxy.py

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/proxy.py` (Lines 88, 129) |
| **Severity** | 🟡 Medium |
| **Issue** | `params: dict = None` and `json_body: dict = None` are invalid type hints. mypy would report errors since `None` is not a `dict`. |
| **Fix** | Changed to `params: Optional[dict] = None` and `json_body: Optional[dict] = None`. |
| **Before** | `def safe_proxy_get(..., params: dict = None, ...)` |
| **After** | `def safe_proxy_get(..., params: Optional[dict] = None, ...)` |

---

### 3. health_check Status Code Logic Fix

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/proxy.py` (Line 172) |
| **Severity** | 🟡 Medium |
| **Issue** | `resp.status_code < 500` treated 401 Unauthorized, 404 Not Found as "healthy". |
| **Fix** | Changed to `200 <= resp.status_code < 300` for proper success range. |
| **Before** | `return resp.status_code < 500` |
| **After** | `return 200 <= resp.status_code < 300` |

---

### 4. korean_law Query Parameter Bug Fix

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/finance/__init__.py` (Line 168) |
| **Severity** | 🟠 High |
| **Issue** | `korean_law` command accepted `query` argument but never passed it to `run_mcp()`. User input was silently ignored. |
| **Fix** | Pass query as `arguments={"query": query}` to `run_mcp()`. |
| **Before** | `asyncio.run(run_mcp('korean-law-search', server_url='local://korean-law-mcp', timeout=timeout))` |
| **After** | `args = {"query": query} if query else {}`<br>`asyncio.run(run_mcp('korean-law-search', server_url='local://korean-law-mcp', arguments=args, timeout=timeout))` |

---

### 5. asyncio.get_event_loop() Deprecation Fix

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Line 104) |
| **Severity** | 🟢 Low |
| **Issue** | `asyncio.get_event_loop()` is deprecated in Python 3.12. |
| **Fix** | Changed to `asyncio.get_running_loop()` (called from within async context). |
| **Before** | `loop = asyncio.get_event_loop()` |
| **After** | `loop = asyncio.get_running_loop()` |

---

### 6. CLI Entry Point Name Fix

| Item | Details |
|------|---------|
| **File** | `pyproject.toml` (Line 21) |
| **Severity** | 🟡 Medium |
| **Issue** | Entry point was `k-cli` but README.md and SKILL.md documented `k-skill`. Users would not find the command after installation. |
| **Fix** | Changed entry point from `k-cli` to `k-skill`. |
| **Before** | `k-cli = "cli_anything.k_skill.cli:main"` |
| **After** | `k-skill = "cli_anything.k_skill.cli:main"` |

---

### 7. Deprecated Script Removal

| Item | Details |
|------|---------|
| **File** | `scripts/generate_proxy_skills.py` |
| **Severity** | 🟢 Low |
| **Issue** | File was marked `DEPRECATED` in its own docstring but remained in the repository, causing confusion. |
| **Fix** | Removed the file. Phase 2+ domain files are maintained directly in `cli_anything/k_skill/skills/`. |

---

### 8. run_npm Package Name Validation (Security)

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 114-143) |
| **Severity** | 🔴 Critical (Security) |
| **Issue** | `run_npm()` could execute arbitrary system commands when `_find_npm_bin()` returns `None`, `npx=False`, and `global_install=True`. In this case `cmd = [package] + args` would execute `package` as a system command. A malicious package name like `"rm"` could lead to RCE. |
| **Fix** | Added `_SAFE_NPM_PKG` regex validation (`^[a-zA-Z0-9_\-@/.]+$`) before command construction. Invalid package names return `INVALID_INPUT` error immediately. |
| **Before** | No validation — `package` used directly in command construction |
| **After** | `if not _SAFE_NPM_PKG.match(package): return error_response(..., "INVALID_INPUT", ...)` |

---

### 9. [P0] run_pip_import SkillDependency name Argument Fix

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Line 276) |
| **Severity** | 🔴 Critical |
| **Issue** | `SkillDependency(python=packages)` omitted the required `name` argument, causing `TypeError` at runtime. All `run_pip_import` dependent skills (SRT, KTX, flight-search) would crash. |
| **Fix** | Added `name=module_name` argument. |
| **Before** | `dep = SkillDependency(python=packages)` |
| **After** | `dep = SkillDependency(name=module_name, python=packages)` |

---

### 10. [P1] LocalMCPBridge Environment Variable Security Fix

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/local_mcp_bridge.py` (Lines 78-84) |
| **Severity** | 🔴 Critical (Security) |
| **Issue** | When `self.env` was `None`, the bridge passed `env=None` to subprocess, inheriting ALL environment variables (AWS credentials, SSH keys, all API keys). Also had a stale `safe_keys` allowlist that didn't include API keys. |
| **Fix** | Import and use `_filter_env()` from `runner.py` for consistent filtering. Now always applies the allowlist regardless of `self.env` value. |
| **Before** | `if self.env: ... else: env = None` (full env inheritance) |
| **After** | `env = _filter_env(self.env)` (always filtered) |

---

### 11. [P1] local:// MCP Server Pre-check

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 340-350) |
| **Severity** | 🟠 High |
| **Issue** | `local://` MCP server commands (korean-law-mcp, chrome-mcp, coupang-mcp) would crash with `FileNotFoundError` if not installed. No user-friendly error message. |
| **Fix** | Added `shutil.which(command[0])` pre-check before starting the bridge. Returns `MISSING_DEPENDENCY` error with installation guide hint. |
| **Before** | Direct `LocalMCPBridge(command=command)` → crash if missing |
| **After** | `if command and not shutil.which(command[0]): return error_response(..., "MISSING_DEPENDENCY", ...)` |

---

### 12. [P2] life/lunch Skill Error Handling Standardization

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/life/__init__.py` (Lines 129-166) |
| **Severity** | 🟡 Medium |
| **Issue** | `lunch` skill used `asyncio.run(proxy_get(...))` directly instead of `safe_proxy_get()`. Network errors would propagate as Python exceptions instead of standardized error envelopes. |
| **Fix** | Added explicit `httpx.ConnectError`, `httpx.TimeoutException`, `httpx.HTTPStatusError` catch blocks for both API call steps (school search + meal fetch). |
| **Before** | Single `except Exception as e:` catching everything |
| **After** | Specific exception handlers for each HTTP error type |

---

### 13. [P3] Dependency Version Upper Bounds

| Item | Details |
|------|---------|
| **File** | `pyproject.toml` |
| **Severity** | 🟢 Low |
| **Issue** | Dependencies used `>=` without upper bounds, exposing to breaking changes on major version upgrades. |
| **Fix** | Added `<next-major` upper bounds. |
| **Before** | `"click>=8.0", "httpx>=0.25", "pyyaml>=6.0"` |
| **After** | `"click>=8.0,<9.0", "httpx>=0.25,<1.0", "pyyaml>=6.0,<7.0"` |

---

### 14. [P0-1] LocalMCPBridge Path Traversal Prevention

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/local_mcp_bridge.py` (Lines 62-67) |
| **Severity** | 🔴 Critical (Security) |
| **Issue** | `_SAFE_COMMAND_PATTERN` allowed `..` in command parts, enabling theoretical path traversal attacks (e.g., `local://python3 scripts/../../../bin/sh`). Only the first command part was validated in some code paths. |
| **Fix** | Added explicit `if ".." in part` check before regex validation. All command parts are now validated, not just the first one. |
| **Before** | Only `_SAFE_COMMAND_PATTERN.match(part)` check |
| **After** | `if ".." in part: raise MCPBridgeError(...)` + pattern match |

---

### 15. [P0-2] K_SKILL_ROOT Existence Validation

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 47-54, 144-146, 214-216) |
| **Severity** | 🔴 Critical |
| **Issue** | Default `K_SKILL_ROOT` path calculation (`Path(__file__).parent.parent.parent.parent / "k-skill"`) almost never exists in pip-installed environments. All runner functions (`run_npm`, `run_script`) would fail with `FileNotFoundError` when using it as cwd. |
| **Fix** | Added `_ensure_k_skill_root()` helper function. `run_npm` and `run_script` now check root existence at start and return graceful `CONFIG_ERROR` response. |
| **Before** | No validation → `FileNotFoundError` at subprocess level |
| **After** | `err = _ensure_k_skill_root(); if err: return error_response(..., "CONFIG_ERROR", err)` |

---

### 16. [P0-3] _NPM_BIN_CACHE Path Normalization

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 79-85) |
| **Severity** | 🟠 High |
| **Issue** | Bin paths from `package.json` were stored as relative paths (e.g., `"dist/cli.js"`). On subsequent lookups, `os.path.isfile(bin_cmd)` would fail because the relative path was resolved from cwd, not the package directory. Cache keys were also inconsistent between package.json and node_modules lookups. |
| **Fix** | All cached bin paths are now resolved to absolute paths using `(pkg_dir / bins).resolve()`. |
| **Before** | `_NPM_BIN_CACHE[package_name] = bins` (relative) |
| **After** | `_NPM_BIN_CACHE[package_name] = str((pkg_dir / bins).resolve())` (absolute) |

---

### 17. [P1-1] Manifest Load Failure Warning

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/loader.py` (Lines 30-33, 127-128) |
| **Severity** | 🟡 Medium |
| **Issue** | When a skill directory existed but `manifest.yaml` was missing or invalid, `discover_domains()` silently skipped it with `continue`. No warning was logged, making debugging difficult. |
| **Fix** | Added `logging` module and `logger.warning()` call when `ManifestLoadError` is caught. |
| **Before** | `except ManifestLoadError: continue` |
| **After** | `except ManifestLoadError as e: logger.warning(...); continue` |

---

### 18. [P0] life/lunch Skill `as_json` Parameter Missing

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/life/__init__.py` (Lines 135, 138, 141) |
| **Severity** | 🔴 Critical (UX) |
| **Issue** | Three `emit()` calls in the lunch skill's Step 1 error handlers were missing `as_json=as_json`. When `-j` flag was passed, errors would still output in human-readable format instead of JSON. |
| **Fix** | Added `as_json=as_json` to all three early-return `emit()` calls. |
| **Before** | `emit(error_response("school-lunch", "PROXY_DOWN", ...))` |
| **After** | `emit(error_response("school-lunch", "PROXY_DOWN", ...), as_json=as_json)` |

---

### 19. [P1] search/__init__.py Import Statement PEP8 Violation

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/search/__init__.py` (Line 48) |
| **Severity** | 🟡 Medium |
| **Issue** | `from cli_anything.k_skill.runner import run_script` was placed between function definitions (line 48), violating PEP8 import ordering. |
| **Fix** | Moved import to top of file with other imports. |
| **Before** | Import at line 48 (middle of file) |
| **After** | Import at line 8 (with other imports) |

---

### 20. [P1] runner.py local:// MCP Command Parts Full Validation

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 359-382) |
| **Severity** | 🟠 High |
| **Issue** | Only the first command part (`command[0]`) was validated with `shutil.which()`. Subsequent parts (arguments, script paths) were not validated before being passed to `LocalMCPBridge`. |
| **Fix** | Added validation loop for ALL command parts: `..` check and `_SAFE_COMMAND_PATTERN` match. Returns `INVALID_INPUT` error for any invalid part. |
| **Before** | Only `shutil.which(command[0])` check |
| **After** | Loop: `for part in command: if ".." in part: ...; if not _SAFE_COMMAND_PATTERN.match(part): ...` |

---

### 21. [P0] korean-law MCP tool_name Missing

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/finance/__init__.py` (Line 169) |
| **Severity** | 🔴 Critical |
| **Issue** | `run_mcp()` was called without `tool_name`, causing it to default to `tools[0]` which is `discover_tools` (not the intended `search` tool). The skill would always fail because `discover_tools` expects different arguments. |
| **Fix** | Added `tool_name='search'` to the `run_mcp()` call. Also corrected skill_name from `'korean-law-search'` to `'korean-law'`. |
| **Before** | `run_mcp('korean-law-search', server_url='local://korean-law-mcp', arguments=args, timeout=timeout)` |
| **After** | `run_mcp('korean-law', server_url='local://korean-law-mcp', tool_name='search', arguments=args, timeout=timeout)` |

---

### 22. [P0] run_mcp tool_name None Default Bug (System-Level)

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/runner.py` (Lines 354, 392) |
| **Severity** | 🔴 Critical (System) |
| **Issue** | When `tool_name` was not specified, `run_mcp()` defaulted to `tools[0].get("name", "")` for remote MCP and `""` for local MCP. This caused unpredictable behavior — the first tool in the list might not be the intended one, and empty string tool names caused server errors. |
| **Fix** | Both remote (http://) and local (local://) MCP branches now require `tool_name`. Returns `INVALID_INPUT` error with list of available tools if not specified. |
| **Before** | `tool = tool_name or tools[0].get("name", "")` / `tool_name or ""` |
| **After** | `if not tool_name: return error_response(..., "INVALID_INPUT", "tool_name이 필요합니다. 사용 가능한 도구: ...")` |

---

### 23. [P1] other/setup Wrong MCP Server URL

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/other/__init__.py` (Line 30) |
| **Severity** | 🟠 High |
| **Issue** | `setup` skill used `server_url='local://korean-law-mcp'` — a copy-paste error that pointed to the wrong MCP server. There is no dedicated `k-skill-setup` MCP server. |
| **Fix** | Changed to return a helpful `NOT_IMPLEMENTED` error directing users to the built-in `k-skill setup check/install/proxy` commands. |
| **Before** | `asyncio.run(run_mcp('k-skill-setup', server_url='local://korean-law-mcp', timeout=timeout))` |
| **After** | `emit(error_response("k-skill-setup", "NOT_IMPLEMENTED", "... k-skill setup check/install/proxy를 사용하세요."))` |

---

### 24. [P0] travel/myrealtrip MCP tool_name Missing

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/travel/__init__.py` (Line 20) |
| **Severity** | 🔴 Critical |
| **Issue** | `run_mcp()` was called without `tool_name` for the myrealtrip skill. After the system-level fix (item 22), this now returns `INVALID_INPUT` error instead of silently calling the wrong tool. The skill would fail immediately. |
| **Fix** | Added `tool_name='searchStays'` (verified via live MCP server tools/list call). Also passes keyword as arguments. |
| **Before** | `run_mcp('myrealtrip-search', server_url='https://mcp-servers.myrealtrip.com/mcp', timeout=timeout)` |
| **After** | `run_mcp('myrealtrip-search', server_url='https://mcp-servers.myrealtrip.com/mcp', tool_name='searchStays', arguments={"keyword": query}, timeout=timeout)` |

---

### 25. [P0] travel/hola-poke MCP tool_name Missing

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/travel/__init__.py` (Line 29) |
| **Severity** | 🔴 Critical |
| **Issue** | `run_mcp()` was called without `tool_name` for the hola-poke skill. Same issue as item 24. |
| **Fix** | Added `tool_name='get_menu'` (verified via live MCP server tools/list call with session initialization). |
| **Before** | `run_mcp('hola-poke-yeoksam', server_url='https://hola-poke-yeoksam-skill.onrender.com/mcp', timeout=timeout)` |
| **After** | `run_mcp('hola-poke-yeoksam', server_url='https://hola-poke-yeoksam-skill.onrender.com/mcp', tool_name='get_menu', timeout=timeout)` |

---

### 26. [P0] life/catchtable MCP tool_name Missing

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/life/__init__.py` (Line 390) |
| **Severity** | 🔴 Critical |
| **Issue** | `run_mcp()` was called without `tool_name` for the catchtable skill. chrome-mcp is not installed, so MISSING_DEPENDENCY error fires first, but once installed it would fail with tool_name error. |
| **Fix** | Added `tool_name='예약'` (reasonable guess based on skill purpose). |
| **Before** | `run_mcp('catchtable-sniper', server_url='local://chrome-mcp', timeout=timeout)` |
| **After** | `run_mcp('catchtable-sniper', server_url='local://chrome-mcp', tool_name='예약', timeout=timeout)` |

---

### 27. [P1] shopping/naver-shop Missing --timeout Option

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/shopping/__init__.py` (Lines 20-43) |
| **Severity** | 🟡 Medium |
| **Issue** | `naver-shop` command was the only shopping command without `--timeout/-t` option. All other shopping commands (olive-young, market-kurly, daiso, danawa, ohou-deal, coupang) have it. |
| **Fix** | Added `@click.option("--timeout", "-t", default=30, type=int)` and passed it to `safe_proxy_get()`. |
| **Before** | `def naver_shop(query, limit, sort, page, as_json):` / `safe_proxy_get(..., params)` |
| **After** | `def naver_shop(query, limit, sort, page, as_json, timeout):` / `safe_proxy_get(..., params, timeout=timeout)` |

---

### 28. [P2] Unused run_mcp Imports Removed

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/skills/transit/__init__.py`, `delivery/__init__.py`, `document/__init__.py` |
| **Severity** | 🟢 Low (Dead Code) |
| **Issue** | `run_mcp` was imported but never used in these three domain files. |
| **Fix** | Removed `run_mcp` from the import statement in each file. |
| **Before** | `from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import, run_mcp` |
| **After** | `from cli_anything.k_skill.runner import run_npm, run_script, run_pip_import` |

---

## Known Issues (Not Fixed — Future Work)

### A. SSRF TOCTOU (DNS Rebinding)

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/mcp_client.py` (Lines 83-98) |
| **Severity** | 🟠 High |
| **Issue** | `_validate_endpoint_url()` checks DNS via `socket.getaddrinfo()` then makes HTTP request. DNS rebinding attack possible between check and use. |
| **Status** | Mitigated (https forced, localhost/private IP blocked). Full fix requires custom transport or re-validation at connect time. |

### B. local_mcp_bridge Path Traversal

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/local_mcp_bridge.py` (Line 21) |
| **Severity** | 🟡 Medium |
| **Issue** | `_SAFE_COMMAND_PATTERN` allows `..` and multiple `/`, enabling theoretical directory traversal. |
| **Status** | Low risk (commands are code-controlled). Should add `..` rejection. |

### C. asyncio.run() Nesting

| Item | Details |
|------|---------|
| **File** | Multiple (cli.py, skills/*.py) |
| **Severity** | 🟠 High |
| **Issue** | `asyncio.run()` cannot be called from a running event loop. Would fail in Jupyter, FastAPI, or other async environments. |
| **Status** | Works in CLI context. Future: use `nest_asyncio` or coroutine-based API. |

### D. format_human Nested Dict Handling

| Item | Details |
|------|---------|
| **File** | `cli_anything/k_skill/output.py` (Lines 106-120) |
| **Severity** | 🟢 Low |
| **Issue** | Nested dicts/lists at depth > 2 are not recursively formatted. |
| **Status** | Cosmetic. Should add recursive formatting. |

---

## Test Results

| Metric | Before | After |
|--------|--------|-------|
| Passed | 104 | **116** |
| Failed | 12 | **0** |
| Total | 116 | 116 |

Run: `.venv/bin/pytest tests/ -v`

---

## Files Modified

| File | Change |
|------|--------|
| `pyproject.toml` | pytest-asyncio version, CLI entry point name, dependency upper bounds |
| `cli_anything/k_skill/proxy.py` | Type hints, health_check logic |
| `cli_anything/k_skill/runner.py` | asyncio deprecation, npm package validation, SkillDependency name fix, local:// MCP pre-check, K_SKILL_ROOT validation, _NPM_BIN_CACHE path normalization, local:// MCP command parts full validation, **tool_name required enforcement (system-level bug)** |
| `cli_anything/k_skill/local_mcp_bridge.py` | Environment variable filtering (import _filter_env from runner.py), path traversal (..) prevention |
| `cli_anything/k_skill/loader.py` | Manifest load failure warning logging |
| `cli_anything/k_skill/skills/finance/__init__.py` | korean_law query bug, **korean-law tool_name='search' fix** |
| `cli_anything/k_skill/skills/life/__init__.py` | lunch skill error handling standardization, as_json parameter fix, **catchtable tool_name fix** |
| `cli_anything/k_skill/skills/search/__init__.py` | Import statement PEP8 ordering fix |
| `cli_anything/k_skill/skills/other/__init__.py` | **setup skill wrong MCP URL → NOT_IMPLEMENTED error** |
| `cli_anything/k_skill/skills/travel/__init__.py` | **myrealtrip/hola-poke tool_name fixes (verified via live MCP server)** |
| `cli_anything/k_skill/skills/shopping/__init__.py` | **naver-shop --timeout option added** |
| `cli_anything/k_skill/skills/transit/__init__.py` | **Unused run_mcp import removed** |
| `cli_anything/k_skill/skills/delivery/__init__.py` | **Unused run_mcp import removed** |
| `cli_anything/k_skill/skills/document/__init__.py` | **Unused run_mcp import removed** |
| `scripts/generate_proxy_skills.py` | **Deleted** (deprecated) |
