"""Chapter 4: Time, Cohorts, Transitions, and Competing Events.

Standalone construction code: no creditriskbook imports.
"""

from collections import Counter, defaultdict

histories = {
    "A": ["current", "current", "30_dpd", "60_dpd"],
    "B": ["current", "30_dpd", "current", "current"],
    "C": ["current", "current", "prepaid", "prepaid"],
}
transition_counts = defaultdict(Counter)

for states in histories.values():
    for current_state, next_state in zip(states, states[1:], strict=False):
        transition_counts[current_state][next_state] += 1

for current_state, counts in transition_counts.items():
    row_total = sum(counts.values())
    probabilities = {
        next_state: round(count / row_total, 3) for next_state, count in sorted(counts.items())
    }
    print(current_state, probabilities, "row sum=", round(sum(probabilities.values()), 3))
