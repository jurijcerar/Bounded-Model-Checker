# Python Bounded Model Checker for NuSMV-like Models

This repository contains a **Python implementation of a bounded model checker (BMC)** for Linear Temporal Logic (LTL) specifications over a NuSMV-like modeling language. The tool automatically parses models, encodes them into SMT, and checks LTL properties using bounded model checking with ((k, l))-loops.

A Jupyter notebook, **`demo.ipynb`**, is included to demonstrate how to use the implementation on several example models.

---

## Overview

The model checker:

* Reads NuSMV-like input files
* Builds a symbolic transition system
* Encodes bounded executions with ((k, l))-loops into SMT
* Checks whether LTL specifications hold for all executions up to a given bound (k)

The implementation is intended to be simple, explicit, and easy to extend.

---

## Supported NuSMV-like Language Features

### Modules

* Exactly one `MODULE main`

### Variable Declarations

* **Boolean variables**

  ```smv
  VAR x: boolean; y: boolean;
  ```

* **Enumeration variables**

  ```smv
  VAR proc: {idle, entering, critical, exiting};
  ```

### State Constraints

* **Initial conditions (`INIT`)**

  ```smv
  INIT proc = idle
  ```

* **Transition relations (`TRANS`)**, including nondeterministic updates

  ```smv
  TRANS proc = critical -> next(proc) in {critical, exiting}
  ```

* **Invariants (`INVAR`)**

  ```smv
  INVAR proc = critical -> x & y
  ```

### Expressions

The following expression forms are supported:

* Variables declared with `VAR`
* Constants: `TRUE`, `FALSE`, and enumeration constants
* Comparisons: `=`, `!=`
* Boolean combinations: `!`, `&`, `|`, `->`
* Set inclusion:

  ```smv
  proc in {idle, entering}
  ```

---

## Supported LTL Operators

The bounded model checker supports the following LTL operators:

* `X` – next
* `G` – globally
* `F` – finally
* `U` – until
* `V` – release
* `!` – negation
* `&` – conjunction
* `|` – disjunction
* `->` – implication

The **Until (`U`)** and **Release (`V`)** operators are fully implemented using standard bounded semantics over ((k, l))-loops.

---

## Examples

Several example models are included in the `examples/` directory and can be used to test the checker. These cover:

* Safety properties
* Liveness properties
* Models using the `U` (until) operator

The `demo.ipynb` notebook walks through loading a model, setting a bound (k), and checking whether the given LTL specification holds.

---

