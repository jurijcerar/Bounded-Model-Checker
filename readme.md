# Python Bounded Model Checker for NuSMV-like Models

A Python implementation of a **Bounded Model Checker (BMC)** for LTL specifications over a NuSMV-like modeling language. The tool parses `.smv` files, encodes bounded executions into SMT constraints, and checks LTL properties using Z3.

---

## Installation

```
pip install z3-solver lark
```

---

## Usage

```python
import parse
from bmc import BoundedModelChecker

with open('examples/short.smv') as f:
    smv_model = parse.parse(f.read())

bmc = BoundedModelChecker(smv_model)

for k in range(1, 10):
    for l in range(1, k + 1):
        bmc.check(k, l)
        for modl in bmc.model:
            if modl is not None:
                print(f'Specification({k}, {l}) is not satisfied')
                bmc.print_model(k, modl)
                exit()

print('Specification holds')
```

`bmc.check(k, l)` checks all LTL specifications against a `(k, l)`-loop — a path of length `k` that loops back to step `l`. If any specification has a counterexample, `bmc.model` contains it. Iterate over increasing `k` and `l` until a counterexample is found or the bound is exhausted.

---

## Input Format

Files follow a subset of the NuSMV language. Only one `MODULE main` is supported.

### Variable declarations

```smv
VAR
    x       : boolean;
    state   : {idle, running, done};
    counter : 0 .. 15;
    n       : integer;
```

Supported types: `boolean`, named enumerations `{a, b, c}`, bounded integer ranges `lo .. hi`, and unbounded `integer`.

### Constraints

```smv
INIT state = idle & counter = 0

TRANS state = idle -> next(state) = running
TRANS state = running -> next(counter) = counter + 1

INVAR counter >= 0
```

- `INIT` — initial state condition (no `next()` allowed)
- `TRANS` — transition relation; `next(v)` refers to the value of `v` in the next step
- `INVAR` — invariant that must hold at every step (no `next()` allowed)

Multiple `INIT`, `TRANS`, and `INVAR` declarations are ANDed together.

### Expressions

| Form | Example |
|------|---------|
| Boolean variable | `x`, `TRUE`, `FALSE` |
| Enum variable / value | `state = idle` |
| Integer arithmetic | `counter + 1`, `y mod 16`, `a * b - c` |
| Arithmetic comparison | `counter >= 10`, `y != 7` |
| Boolean operators | `!`, `&`, `|`, `->` |
| Set membership | `state in {idle, running}` |
| Next value | `next(x)`, `next(counter)` |

### LTL specifications

```smv
LTLSPEC G (request -> F state = done)
```

Multiple `LTLSPEC` declarations are checked independently — a counterexample is reported for the first one that fails.

---

## LTL Operators

### Future operators

| Operator | Syntax | Meaning |
|----------|--------|---------|
| Next | `X φ` | φ holds at the next step |
| Globally | `G φ` | φ holds at every future step |
| Finally | `F φ` | φ holds at some future step |
| Until | `φ U ψ` | φ holds until ψ becomes true |
| Release | `φ V ψ` | ψ holds until (and including) φ; if φ never holds, ψ holds forever |
| Not | `! φ` | negation |
| And / Or / Implies | `φ & ψ`, `φ | ψ`, `φ -> ψ` | boolean connectives |

### Past operators

Past operators reason about the history of the execution up to the current step.

| Operator | Syntax | Meaning |
|----------|--------|---------|
| Yesterday | `Y φ` | φ held at the previous step; `False` at step 0 |
| Once | `O φ` | φ held at some past step (including now) |
| Historically | `H φ` | φ held at every past step (including now) |

```smv
-- alarm only turns on after the sensor was triggered
LTLSPEC G (alarm -> O sensor)

-- alarm has never fired if sensor has always been off
LTLSPEC G (H !sensor -> !alarm)
```

---

## Fairness Constraints

Fairness constraints restrict which execution paths are considered. Only **fair** paths satisfy all fairness constraints and are checked against LTL specifications.

```smv
-- Justice: proc1 reaches critical infinitely often
FAIRNESS proc1 = critical
JUSTICE  proc2 = critical

-- Compassion: if p holds infinitely often, so must q
COMPASSION (proc = entering, proc = critical)
```

`FAIRNESS` and `JUSTICE` are synonyms. A path is fair iff every justice constraint holds at some step in each loop, and every compassion constraint `(p, q)` satisfies: if `p` holds in the loop then `q` must too.

---

## Integer Arithmetic

Integer variables support `+`, `-`, `*`, `/`, `mod` and comparisons `=`, `!=`, `<`, `<=`, `>`, `>=`. Bounded range types `lo .. hi` add constraints automatically.

```smv
MODULE main
VAR y : 0 .. 15;
INIT y = 0
TRANS y = 7  -> next(y) = 0
TRANS y != 7 -> next(y) = ((y + 1) mod 16)
LTLSPEC G (y = 4 -> X y = 6)
```

---

## Examples

All examples are in the `examples/` directory.

| File | What it demonstrates |
|------|---------------------|
| `short.smv` | Boolean/enum model; G, F, X operators |
| `ferryman.smv` | Ferryman puzzle; F reachability |
| `ferrymanuntil.smv` | Ferryman puzzle using the Until operator |
| `release.smv` | Release operator (V) |
| `hanoi.smv` | Towers of Hanoi, 4 disks |
| `fairness.smv` | Mutual exclusion with FAIRNESS constraints |
| `past_operators.smv` | Past operators Y, O, H |
| `counter.smv` | Integer counter with mod arithmetic |
| `zune_bug.smv` | The Zune firmware bug via integer arithmetic |

---
