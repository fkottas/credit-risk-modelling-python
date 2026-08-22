# Academic writing, evidence, and teaching standard

This book is written as an academic and professional textbook, not as product documentation.
Technical accuracy comes first, but accuracy alone is insufficient: the reader must be able to
understand why a method is needed, how it is derived, what its output means, and when the method
can fail.

## 1. Required reasoning sequence

Each chapter follows the same intellectual sequence without repeating identical prose:

1. **Question and purpose.** State the credit, accounting, capital, validation, or operational
   question in ordinary professional language. Explain why the question matters before presenting
   a formula or control.
2. **Definitions and observation design.** Define the population, observation unit, reference date,
   information set, outcome, and horizon. Terms such as default, cure, Stage 2, downturn, approval,
   and loss are not used without an operational definition.
3. **Mathematical development.** Introduce notation, state assumptions, derive the result in logical
   steps, and provide a symbol table when several quantities are involved. Distinguish an identity,
   an estimator, an approximation, and a policy convention.
4. **Worked example.** Use values small enough to verify manually. Show intermediate quantities,
   units, and the expected numerical answer.
5. **Python implementation.** Present the transparent implementation before the reusable project
   class or function. Display executed output and test at least one invariant or boundary condition.
6. **Interpretation.** Explain what changes when an input changes, what the output does and does not
   establish, and how the result affects a real modelling or review decision.
7. **Assumptions and limitations.** Identify sampling, timing, measurement, legal, statistical, and
   implementation limitations. Do not use generic warnings in place of method-specific analysis.
8. **Evidence and further work.** Cite the primary regulation, original method, authoritative data
   record, or peer-reviewed literature supporting material claims. Exercises extend the reasoning;
   they do not merely ask the reader to rerun code.

## 2. Evidence hierarchy

Every material statement belongs to one of the following classes. The wording and citation must
make the class clear.

| Statement class | Appropriate support | Required wording discipline |
|---|---|---|
| Mathematical identity | derivation or original statistical source | state domains and assumptions |
| Empirical result | executed code, stated sample, metric and split | never generalise beyond the data |
| Regulatory or accounting requirement | current primary legal, regulatory or standard-setter text | use “requires” only when the source is normative |
| Supervisory expectation | official supervisory guidance | distinguish it from legislation and accounting standards |
| Project design choice | reasoned author decision plus tests | call it a convention or implementation choice |
| Illustrative assumption | hand-worked or synthetic example | label it illustrative; do not present it as an industry estimate |
| Interpretation or inference | cited evidence plus explicit reasoning | identify the inferential step and alternatives |

Unverified claims, universal performance improvements, unsupported thresholds, and causal language
from predictive associations are excluded. A numerical claim must be reproducible from committed
code or attributed to a source.

## 3. Language and terminology

- Prefer established terms used in statistics, accounting, banking, software engineering, and law.
- Define specialist terms at first use. Use the same term for the same concept throughout the book.
- Prefer a direct causal explanation to a slogan. For example, explain that a time split is needed
  because future observations must not influence model development; do not call the split a “gate.”
- Avoid private metaphors and internal shorthand such as *control spine*, *operating system*,
  *evidence pack*, *frozen artifact*, or *bounded agent* when conventional terms—framework,
  documentation set, approved model version, or restricted-authority agent—are clearer.
- Use *must* only for a mathematical necessity, legal or accounting requirement, or explicitly
  adopted project rule. Use *should* for a recommendation and explain the reason.
- Avoid repetitive contrasts such as “not only,” “does not automatically,” and “silently.” State the
  positive rule and then the consequence of violating it.
- Main chapter prose explains the subject. Meta-commentary about what “the laboratory starts with,”
  what “the repository deliberately does,” or what will be introduced later belongs in a short
  implementation note, not in the conceptual explanation.
- Paragraphs begin with a clear proposition, develop one line of reasoning, and end with its
  implication. Lists are used only when the items are genuinely parallel.

## 4. Mathematics and code

Displayed mathematics must remain native Word mathematics in the review document. Every principal
formula is accompanied by definitions, units or dimensions, admissible domains, derivation, a small
calculation, and at least one testable implication. Code follows the mathematical notation where
practical and identifies unavoidable differences such as zero-based indexing, floating-point
tolerance, clipping, or missing-value representation.

Chapters 1–24 contain standalone implementations and do not import `creditriskbook`. Chapters
25–54 show the method-specific implementation before promoting it to the project package. Chapters
55–72 may use the reviewed package for integration, validation, deployment, and agent workflows,
while still exposing the calculation or decision rule being examined.

## 5. Figures and tables

- A figure answers a specific question that prose alone would explain less efficiently.
- Titles describe the relationship shown; captions explain why it matters. Neither uses generic
  labels such as “original teaching visual.”
- Legends are placed outside the data region or replaced with direct labels. An annotation may not
  cover a bar, point, curve, axis label, or another annotation.
- Figures use a restrained colour-blind-safe palette, readable type, light grid lines, explicit units,
  and sufficient margins for Word placement.
- Tables are reserved for repeated fields or comparisons. Column widths follow content, numeric
  columns identify units, and long explanatory prose remains outside the table.

## 6. Dataset reporting

The book distinguishes four states: **catalogued**, **downloadable by reviewed code**, **used in an
executed example**, and **reference-only or conditional**. Public availability is not treated as a
licence. Every empirical exercise records publisher, official URL, licence or governing terms,
access date, checksum where feasible, target meaning, observation unit, period, limitations, and
whether raw redistribution is permitted.

Synthetic datasets are generated independently for clearly defined teaching questions. They do not
copy rows, identifiers, text, or rare combinations from a source dataset. If a generator is informed
by external data, the source licence must permit derivative use and the method must include
disclosure-risk tests. Deliberately defective datasets use a defect manifest that records each
introduced error, its rationale, expected detection rule, and corrected outcome.

## 7. Release checks

Before publication, the project must pass:

1. manuscript structure, citation, terminology, and formula audits;
2. execution of all displayed code and notebooks;
3. unit, integration, and approved live-data tests;
4. figure overlap and legend-placement checks;
5. Word navigation, native-equation, table-geometry, accessibility, and page-density audits; and
6. complete page-by-page rendered visual inspection.
