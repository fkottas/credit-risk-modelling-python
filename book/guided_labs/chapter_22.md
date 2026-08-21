## Mathematics-to-code laboratory — observation and outcome windows

### 1. Draw the timeline

For each row label the lookback $(t-w,t]$, buffer $(t,t+g]$ and performance window $(t+g,t+g+h]$. Place events exactly on every boundary and predict their labels before writing code.

### 2. Build the target from raw events

Implement $Y_i=\mathbb{1}\{t_i+g<\tau_i\le t_i+g+h\}$. Preserve observation identifier, customer, reference date, event date, maturity flag and trigger reason. Multiple default events collapse to one binary label only after the rule is evaluated.

### 3. Prove label maturity

Given extraction date $T$, assert $t_i+g+h\le T$ for binary-model rows. Do not turn censored observations into non-defaults. Compare the event rate before and after an intentionally incorrect immature-label treatment.

### 4. Split at the right unit

Compare random-row, grouped-customer and out-of-time splits. Assert no customer appears on both sides of a grouped split. Fit preprocessing on training only. Explain why a higher random-row result is not stronger evidence when customers repeat.

### 5. Promote and document

Move the tested target builder into the student's library. Store default-definition version, window boundaries, extraction date, exclusions, maturity counts and code commit in the run manifest.
