# Source and evidence policy

## Source hierarchy

1. **Binding or authoritative material:** legislation, accounting standards, Basel Framework chapters, regulator guidance, and official dataset records.
2. **Primary research:** peer-reviewed papers with identifiable data, methods, results, and reproducible definitions.
3. **Professional interpretation:** recognised audit, consulting, and industry guides, used as secondary explanation rather than the legal or accounting authority.
4. **Teaching resources and repositories:** used for comparison or inspiration only when their licences permit it. Their text, figures, and code are not copied without permission.

Every chapter must separate requirements from interpretation and the author's implementation choice. Regulatory statements must include jurisdiction, version or effective date, and access date.

## Dataset acceptance gate

A dataset is rejected or made conditional if any of the following is missing:

- an identifiable publisher or creator;
- an authoritative landing page;
- an explicit licence or terms of use;
- permission compatible with the planned use;
- a feasible attribution statement;
- sufficient definitions to construct the target without guessing.

Kaggle is an access platform, not automatically the original rights holder. If a dataset mirrors UCI, a government portal, a lender, or a competition, the original terms control whenever they are more restrictive. Competition data are never bundled by default.

## Reproducibility record

Each empirical run records the dataset key, source URL, access date, local SHA-256 digest, loader version, target definition, observation and performance windows, filters, random seed, package versions, and Git commit. Modifications such as injected missingness are labelled explicitly.

## Copyrighted attachments

The attached Siddiqi book and PwC guide are copyrighted. They may support original explanations and citations, but their prose, tables, figures, and worked examples will not be reproduced. The attached Basel Committee validation study is an authoritative historical source but will be checked against the current consolidated Basel Framework.

The attached third-party project archive identifies Andrija Djurovic's book repository and does not expose a blanket repository licence in its top-level material. Only separately licensed components can be considered under their own licences. Nothing from the archive is copied into this project.

## Agentic-AI paper evidence review

The attached paper *Agentic AI for Autonomous, Explainable, and Real-Time Credit Risk Decision-Making* is treated as a conceptual source only. Its PDF states a December 2024 publication date while its reference list largely cites 2025 publications. It reports metrics from an unspecified loan-applicant dataset and describes charts created in Excel without enough information to reproduce the experiment. Consequently, its accuracy, latency, and explainability numbers are not used as evidence in this book.

