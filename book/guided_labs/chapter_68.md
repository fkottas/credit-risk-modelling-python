## Worked calculation — How are document fields and policy passages extracted while preserving source provenance?

A claim is reviewable only when it links to the correct document, page, offsets, version, and access rights.

**Companion case:** `synthetic_credit_documents`. **Implementation level:** Applied implementation: the code creates a reproducible validation, deployment, or governance record while keeping measurement separate from policy authority.

### Method

The calculation follows

\[
BM25(q,d)=\sum_{t\in q}idf(t)\frac{f(t,d)(k_1+1)}{f(t,d)+k_1(1-b+b|d|/\overline{|d|})}
\]


### Python implementation

```python
import math
import re
from collections import Counter


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25(query, documents, k1=1.5, b=0.75):
    doc_tokens = [tokens(document) for document in documents]
    average_length = sum(map(len, doc_tokens)) / len(doc_tokens)
    scores = []
    for document in doc_tokens:
        counts = Counter(document)
        score = 0.0
        for term in set(tokens(query)):
            document_frequency = sum(term in item for item in doc_tokens)
            inverse_document_frequency = math.log(
                1 + (len(documents) - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            frequency = counts[term]
            denominator = frequency + k1 * (1 - b + b * len(document) / average_length)
            score += inverse_document_frequency * frequency * (k1 + 1) / denominator
        scores.append(score)
    return scores


policy = [
    "verified income evidence is required before affordability review",
    "applications with missing identity evidence must be referred",
    "model deployment requires independent validation approval",
]
scores = bm25("what income evidence is required", policy)
ranking = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
print([(index, round(score, 4), policy[index]) for index, score in ranking])
```

### Executed result

```output
[(0, 3.2784, 'verified income evidence is required before affordability review'), (1, 0.4515, 'applications with missing identity evidence must be referred'), (2, 0.0, 'model deployment requires independent validation approval')]
```

### Interpretation

BM25 ranks the verified-income passage first with a substantially higher score than the other passages. Retrieval relevance still requires an adjudicated support judgement.

**Validation:** Measure field accuracy, retrieval recall, citation support, and as-of-date validity.

### Exercises

1. Repeat the calculation with **synthetic documents and SEC filings retrieved under fair-access rules** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
