"""Chapter 1: Credit Risk as Uncertain Cash Flows.

Standalone construction code: no creditriskbook imports.
"""

schedule = [
    # month, contractual, received, recovery, workout cost
    (1, 350.0, 350.0, 0.0, 0.0),
    (2, 350.0, 200.0, 0.0, 5.0),
    (3, 350.0, 0.0, 120.0, 15.0),
]
eir = 0.12
total_pv_loss = 0.0

print("month  shortfall  discount  pv_loss")
for month, contractual, received, recovery, cost in schedule:
    shortfall = contractual - received - recovery + cost
    discount = (1.0 + eir) ** (-month / 12.0)
    pv_loss = shortfall * discount
    total_pv_loss += pv_loss
    print(f"{month:>5}  {shortfall:>9.2f}  {discount:>8.4f}  {pv_loss:>7.2f}")

print("Total PV loss:", round(total_pv_loss, 2))
