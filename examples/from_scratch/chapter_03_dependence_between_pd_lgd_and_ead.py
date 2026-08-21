"""Chapter 3: Dependence Between PD, LGD, and EAD.

Standalone construction code: no creditriskbook imports.
"""

scenarios = [
    # name, weight, PD, LGD, EAD
    ("base", 0.60, 0.03, 0.35, 10_000.0),
    ("downturn", 0.25, 0.09, 0.50, 11_000.0),
    ("severe", 0.15, 0.20, 0.65, 12_000.0),
]

coherent_el = 0.0
average_pd = average_lgd = average_ead = 0.0
for name, weight, pd, lgd, ead in scenarios:
    scenario_el = pd * lgd * ead
    coherent_el += weight * scenario_el
    average_pd += weight * pd
    average_lgd += weight * lgd
    average_ead += weight * ead
    print(name, "EL=", round(scenario_el, 2), "weighted EL=", round(weight * scenario_el, 2))

product_of_averages = average_pd * average_lgd * average_ead
print("Weighted scenario EL:", round(coherent_el, 2))
print("Product of separate averages:", round(product_of_averages, 2))
print("Dependence effect:", round(coherent_el - product_of_averages, 2))
