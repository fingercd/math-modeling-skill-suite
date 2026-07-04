---
name: math-modeling-research
description: Use when researching a mathematical modeling contest problem, selecting a topic or direction, searching algorithms/models/industry cases, and maintaining research/research.md for reproducible handoff.
---

# Math Modeling Research

## Stage Label

Use only in `(全网广泛调研)` unless the suite controller asks for a targeted follow-up. Start each response with `(全网广泛调研)`.

## Research Order

1. Confirm the problem choice, broad research direction, known data, and target contest.
2. Split the problem into subquestions, inputs, outputs, constraints, and evaluation indicators.
3. Search three required resource classes:
   - algorithm papers: methods, assumptions, metrics, limitations
   - modeling papers: contest theses, comparable mathematical models
   - industry practice cases: domain workflows, operational constraints, practical indicators
4. Use these priority channels: Kaggle, GitHub, CSDN, Google Scholar.
5. Supplement with official contest rules, excellent-paper repositories, arXiv/CNKI-style paper sources when available, industry reports, government/open datasets, and documentation.
6. End with candidate modeling routes and tradeoffs, but do not lock the final route until the user confirms.

During an active official contest, avoid public posting or discussion of live problem content. Prefer searching general methods, historical cases, public datasets, and domain background.

## research.md Contract

Maintain `research/research.md` after every user turn. Use `../templates/stage-files/research.md` as the starting template.

Each update must include:

- problem selection and research direction
- user changes or new ideas
- search queries and channels used
- sources grouped as algorithm papers, modeling papers, industry cases, datasets/tools
- extracted methods and assumptions
- methods rejected and why
- candidate routes per subquestion
- next gate question for the user

Write enough detail that a teammate can reproduce the search path and reasoning.

## Output Shape

Return a compact synthesis:

- `已确认`: problem, data, constraints
- `资料证据`: strongest sources and why they matter
- `候选方法`: options per problem module
- `推荐方向`: one recommended route with risk notes
- `需用户确认`: decisions needed before `(建模思路与论文框架)`

Include URLs for web sources. Do not cite sources you have not opened or verified.
