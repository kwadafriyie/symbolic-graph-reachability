# Symbolic Graph Reachability with BDDs

Answers reachability questions about a directed graph without ever walking it node by node. The graph, its node sets, and its paths are encoded as Boolean formulas and stored as **binary decision diagrams (BDDs)**, so every operation works on whole sets at once.

Built for CptS 350 (Design and Analysis of Algorithms) at Washington State University, Fall 2026.

## The problem

- **Graph G:** 32 nodes (0–31). Every node `i` has edges to `(i + 3) % 32` and `(i + 8) % 32`.
- **Sets:** `EVEN` = even nodes; `PRIME` = {3, 5, 7, 11, 13, 17, 19, 23, 29, 31}.
- **Question (StatementA):** does every prime node reach some even node in a positive even number of steps?

```
∀u. PRIME(u) → ∃v. EVEN(v) ∧ RR2star(u, v)
```

DFS/BFS is off limits. The answer has to come from symbolic operations on BDDs.

## Approach

| Step | Idea | Result |
|---|---|---|
| Encode nodes | 32 nodes → 5 bits each; a node is a minterm (AND of literals) | `node(i, v)` |
| Encode sets | OR of node minterms | `EVEN`, `PRIME` |
| Encode edges | source on `x[0..4]`, destination on `y[0..4]`; R = OR of all 64 edges | `RR` |
| Two steps | composition: `∃z. R(x,z) ∧ R(z,y)` | `RR2` |
| Closure | repeat `H := H ∨ (H ∘ RR2)` until the BDD stops changing (fixed point) | `RR2star` |
| Statement | inner `∃` by smoothing; `→` as `¬P ∨ Q`; `∀` as `¬∃¬` | constant BDD: true/false |

Once both quantifiers are eliminated, no variables remain, so StatementA reduces to the constant 0 or 1 BDD.

## Results

```
RR(27, 3)  = True
RR(16, 20) = False
edges in RR: 64
EVEN(14)  = True
EVEN(13)  = False
PRIME(7)  = True
PRIME(2)  = False
RR2(27, 6) = True
RR2(27, 9) = False
pairs in RR2: 96
closure rounds: 9
pairs in RR2star: 1024
RR2star is constant TRUE: True
StatementA = True
```

The closure covers all 32 × 32 = 1024 pairs: every node reaches every node in some positive even number of steps. So StatementA is **true**.

## Run it

Requires Python 3 and [pyEDA](https://pyeda.readthedocs.io/). pyEDA compiles C extensions, so Linux or WSL is the easiest setup.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 project.py
```

## Background

This is the core technique of **symbolic model checking** (Bryant's BDDs, 1986; Burch, Clarke, McMillan et al., 1990), used in the chip industry to verify hardware designs whose state spaces are far too large to enumerate.
