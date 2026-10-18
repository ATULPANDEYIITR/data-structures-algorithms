# Recursion Trees

## Purpose

A recursion tree represents the execution structure of a recursive algorithm. Each node corresponds to one recursive call, and each child corresponds to a recursive call made by that parent.

The useful information is not simply that an algorithm is recursive. A recursion tree exposes:

- how many recursive branches each call creates;
- how quickly the input or state becomes smaller;
- how much work is performed at each node;
- how deep the recursion becomes;
- how many terminal calls exist;
- whether different branches evaluate the same state;
- and how the work accumulated across the tree relates to a recurrence.

The six deliverables use different technical perspectives. Python builds and analyzes explicit execution trees, JavaScript combines tree modeling with event-driven and asynchronous recursion, C++ models recursive execution as a validation-system case study, Java represents recursive execution using an enterprise-style domain model, and PostgreSQL stores recursive call relationships for database-level analysis.

---

## Core recursion-tree model

A recursive call can be viewed as a node:

`T(n)`

If that call invokes two smaller problems, the children might be:

`T(n-1)` and `T(n-2)`

The resulting structure is:

```text
T(n)
├── T(n-1)
│   ├── ...
│   └── ...
└── T(n-2)
    ├── ...
    └── ...
