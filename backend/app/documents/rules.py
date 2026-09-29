"""A tiny, safe rule DSL for contract checks - never `eval`.

A rule is plain data (from the checklist YAML) evaluated against a dict of
extracted facts (`{fact_name: value}`, value None = "not found in contract").

    leaf     {field: probation_months, max: 6}
             {field: has_termination_clause, required: true}
             {field: allows_penalty_salary_deduction, forbidden: true}
             {field: governing_law, present_any: [governing_law, jurisdiction]}
             {field: noncompete_duration_months,
              required_if: {field: has_noncompete_clause, truthy: true}}
    all_of   {all_of: [rule, rule, ...]}
    any_of   {any_of: [rule, rule, ...]}

Leaf operators: max, min, gt, lt, equals, not_equals, one_of, truthy, falsy,
required, forbidden, present_any, required_if. A leaf has one `field`
(omitted only for `present_any`, which names its own fields) and exactly one
operator. `required_if` takes a leaf-shaped condition (`field` + operator).

evaluate() returns one of:
    PASS       the rule is satisfied
    VIOLATION  the fact was found and breaks the rule (e.g. 8 > max 6)
    ABSENT     the fact needed to judge the rule was not found in the contract

Keeping "found and wrong" apart from "not found" is what lets the audit say
"probation is 8 months (max 6)" for one and "no dispute-resolution clause" for
the other.
"""
from __future__ import annotations

from typing import Any

PASS = "pass"
VIOLATION = "violation"
ABSENT = "absent"

_NUMERIC_OPS = {"max", "min", "gt", "lt"}
_VALUE_OPS = {"equals", "not_equals", "one_of"}
_FLAG_OPS = {"truthy", "falsy", "required", "forbidden"}
_OTHER_OPS = {"present_any", "required_if"}
LEAF_OPS = _NUMERIC_OPS | _VALUE_OPS | _FLAG_OPS | _OTHER_OPS
COMBINATORS = {"all_of", "any_of"}


class RuleError(ValueError):
    """A malformed rule - raised at checklist load time, never at audit time."""


# ------------------------------------------------------------- validation --

def fields_in(rule: dict) -> set[str]:
    """Every fact name a rule (or `when` guard) reads."""
    out: set[str] = set()
    if not isinstance(rule, dict):
        return out
    for comb in COMBINATORS:
        for sub in rule.get(comb) or []:
            out |= fields_in(sub)
    if "field" in rule:
        out.add(rule["field"])
    if "present_any" in rule:
        out |= set(rule["present_any"])
    if isinstance(rule.get("required_if"), dict):
        out |= fields_in(rule["required_if"])
    return out


def validate(rule: Any, known_facts: set[str] | None = None) -> None:
    """Raise RuleError if `rule` is not a well-formed rule. With
    `known_facts`, also reject a rule reading a fact that isn't declared."""
    if not isinstance(rule, dict) or not rule:
        raise RuleError(f"a rule must be a non-empty mapping, got {rule!r}")
    combs = [c for c in COMBINATORS if c in rule]
    if combs:
        if len(rule) != 1:
            raise RuleError(f"{combs[0]} cannot be mixed with other keys: {sorted(rule)}")
        subs = rule[combs[0]]
        if not isinstance(subs, list) or not subs:
            raise RuleError(f"{combs[0]} needs a non-empty list of rules")
        for sub in subs:
            validate(sub, known_facts)
    else:
        ops = [k for k in rule if k in LEAF_OPS]
        extra = [k for k in rule if k not in LEAF_OPS and k != "field"]
        if extra:
            raise RuleError(f"unknown rule key(s) {extra}; allowed operators: {sorted(LEAF_OPS)}")
        if len(ops) != 1:
            raise RuleError(f"a leaf rule needs exactly one operator, got {ops}: {rule}")
        op = ops[0]
        arg = rule[op]
        if op == "present_any":
            if not isinstance(arg, list) or not arg or not all(isinstance(a, str) for a in arg):
                raise RuleError("present_any needs a non-empty list of fact names")
            if "field" in rule:
                raise RuleError("present_any names its own fields; drop `field`")
        else:
            if not isinstance(rule.get("field"), str):
                raise RuleError(f"leaf rule {rule} needs a `field`")
            if op in _NUMERIC_OPS and (isinstance(arg, bool) or not isinstance(arg, (int, float))):
                raise RuleError(f"{op} needs a number, got {arg!r}")
            if op in _FLAG_OPS and not isinstance(arg, bool):
                raise RuleError(f"{op} needs true/false, got {arg!r}")
            if op == "one_of" and (not isinstance(arg, list) or not arg):
                raise RuleError("one_of needs a non-empty list")
            if op == "required_if":
                validate(arg)
                if "required_if" in arg:
                    raise RuleError("required_if conditions cannot be nested")
    if known_facts is not None:
        unknown = fields_in(rule) - known_facts
        if unknown:
            raise RuleError(f"rule reads undeclared fact(s): {sorted(unknown)}")


# --------------------------------------------------------------- evaluation --

def _present(value: Any) -> bool:
    """A fact counts as found-and-affirmative: True, a non-zero number or a
    non-empty string. None / False / "" / [] mean "not there"."""
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    return float(value) if isinstance(value, (int, float)) else None


def _leaf(rule: dict, facts: dict) -> str:
    if "present_any" in rule:
        return PASS if any(_present(facts.get(f)) for f in rule["present_any"]) else ABSENT
    field = rule["field"]
    value = facts.get(field)
    op = next(k for k in rule if k in LEAF_OPS)
    arg = rule[op]

    if op == "required":
        ok = _present(value)
        return PASS if ok == arg else (ABSENT if arg else VIOLATION)
    if op == "forbidden":
        # forbidden: true -> a truthy value breaks the rule; None is fine
        return VIOLATION if (_present(value) == arg) else PASS
    if op == "truthy":
        return PASS if _present(value) == arg else VIOLATION
    if op == "falsy":
        return PASS if (not _present(value)) == arg else VIOLATION
    if op == "required_if":
        cond = evaluate(arg, facts)
        if cond != PASS:
            return PASS  # condition not met (or unknown): nothing is required
        return PASS if _present(value) else ABSENT

    if op == "not_equals":
        # unlike the other comparisons an unknown fact satisfies this one
        # (None != True), which is what a guard like "not commercial" needs
        return PASS if value != arg else VIOLATION
    if value is None:
        return ABSENT
    if op in _NUMERIC_OPS:
        n = _num(value)
        if n is None:
            return ABSENT
        if op == "max":
            return PASS if n <= arg else VIOLATION
        if op == "min":
            return PASS if n >= arg else VIOLATION
        if op == "gt":
            return PASS if n > arg else VIOLATION
        return PASS if n < arg else VIOLATION  # lt
    if op == "equals":
        return PASS if value == arg else VIOLATION
    if op == "one_of":
        return PASS if value in arg else VIOLATION
    raise RuleError(f"unhandled operator {op}")  # pragma: no cover - validate() prevents this


def evaluate(rule: dict, facts: dict) -> str:
    """PASS / VIOLATION / ABSENT for `rule` against `facts`."""
    if "all_of" in rule:
        results = [evaluate(r, facts) for r in rule["all_of"]]
        if VIOLATION in results:
            return VIOLATION
        return ABSENT if ABSENT in results else PASS
    if "any_of" in rule:
        results = [evaluate(r, facts) for r in rule["any_of"]]
        if PASS in results:
            return PASS
        return VIOLATION if VIOLATION in results else ABSENT
    return _leaf(rule, facts)


def violating_fields(rule: dict, facts: dict) -> list[str]:
    """Facts read by the leaves of `rule` that are found-and-wrong. Lets the
    audit point at the clause that actually breaks an `all_of` rule."""
    if "all_of" in rule or "any_of" in rule:
        out: list[str] = []
        for sub in rule.get("all_of") or rule.get("any_of") or []:
            out.extend(violating_fields(sub, facts))
        return out
    if "field" in rule and _leaf(rule, facts) == VIOLATION:
        return [rule["field"]]
    return []


def applies(guard: dict | None, facts: dict) -> bool:
    """A `when` guard: the check runs only if the guard is definitely met.
    `not_equals: true` on an unknown fact counts as met (None != True)."""
    if not guard:
        return True
    return evaluate(guard, facts) == PASS
