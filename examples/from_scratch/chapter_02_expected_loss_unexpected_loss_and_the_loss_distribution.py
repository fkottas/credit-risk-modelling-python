"""Chapter 2: Expected Loss, Unexpected Loss, and the Loss Distribution.

Standalone construction code: no creditriskbook imports.
"""

from itertools import product

pd = [0.10, 0.20]
loss_if_default = [500.0, 800.0]  # LGD times EAD
distribution = []

for defaults in product((0, 1), repeat=2):
    probability = 1.0
    loss = 0.0
    for default, probability_of_default, amount in zip(defaults, pd, loss_if_default, strict=True):
        probability *= probability_of_default if default else 1.0 - probability_of_default
        loss += default * amount
    distribution.append((loss, probability, defaults))

expected_loss = sum(loss * probability for loss, probability, _ in distribution)
cumulative_probability = 0.0
loss_quantile_95 = None
for loss, probability, defaults in sorted(distribution):
    cumulative_probability += probability
    print(defaults, "loss=", loss, "probability=", round(probability, 3))
    if loss_quantile_95 is None and cumulative_probability >= 0.95:
        loss_quantile_95 = loss

print("Expected loss:", expected_loss)
print("95% loss quantile:", loss_quantile_95)
print("Unexpected loss at 95%:", loss_quantile_95 - expected_loss)
