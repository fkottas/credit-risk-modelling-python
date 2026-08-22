## Worked calculation — Which NLP representation and metric fit a credit-document task?

Classification, extraction, retrieval, and summarisation have different units and error costs.

**Companion case:** `synthetic_credit_documents`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
tfidf(t,d)=tf(t,d)\left[\log\frac{N+1}{df(t)+1}+1\right]
\]


### Python implementation

```python
import math
import re
from collections import Counter


def tokenize(text):
    """Return visible lowercase alphanumeric tokens; preserve the raw text separately."""
    return re.findall(r"[a-z0-9_]+", text.lower())


def tfidf(term, document, corpus):
    tokens = tokenize(document)
    term_frequency = tokens.count(term)
    document_frequency = sum(term in set(tokenize(item)) for item in corpus)
    inverse_document_frequency = math.log((len(corpus) + 1) / (document_frequency + 1)) + 1
    return term_frequency * inverse_document_frequency


corpus = [
    "income verified from payslip",
    "income missing: request payslip",
    "policy requires verified income",
]
print(Counter(tokenize(corpus[0])))
print({"tfidf_income_doc1": round(tfidf("income", corpus[0], corpus), 6)})
```

### Executed result

```output
Counter({'income': 1, 'verified': 1, 'from': 1, 'payslip': 1})
{'tfidf_income_doc1': 1.0}
```

### Interpretation

The tokenizer counts each displayed word and assigns `income` a TF-IDF score of 1.0 in the first document. The value depends on this corpus and tokenisation rule.

**Validation:** Compare tokenisation choices and report class- or field-specific performance.

### Exercises

1. Repeat the calculation with **synthetic credit documents and CFPB complaint text obtained under the current notice** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
