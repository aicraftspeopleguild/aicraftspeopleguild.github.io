"""Test harness: runs TestWrapper cases against Tool UDT instances."""
import json
from pathlib import Path
from tool_runner import load_tool, run_with_logger

def _assert(actual, expect):
    op = expect.get("op", "eq")
    val = expect.get("value")
    if op == "eq":        return actual == val
    if op == "neq":       return actual != val
    if op == "gt":        return actual > val
    if op == "lt":        return actual < val
    if op == "contains":  return val in (actual or "")
    if op == "exists":    return bool(actual)
    return False

def run_tests(tool: dict) -> dict:
    """Execute all TestWrapper cases for this tool. Returns summary dict."""
    cases = tool.get("parameters", {}).get("test_cases") or []
    results = []
    for c in cases:
        name    = c.get("name", "unnamed")
        inputs  = c.get("inputs", {})
        expect  = c.get("expect", {})
        outcome = run_with_logger(tool, inputs)
        # Expect is a dict with {field, op, value} — field is a dotted path into outcome
        field = expect.get("field", "ok")
        cur = outcome
        for part in field.split("."):
            if cur is None: break
            cur = cur.get(part) if isinstance(cur, dict) else None
        passed = _assert(cur, expect)
        results.append({"name": name, "passed": passed, "actual": cur, "expected": expect})
    return {
        "tool":   tool["parameters"]["id"],
        "total":  len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "cases":  results,
    }
