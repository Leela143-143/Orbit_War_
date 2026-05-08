# The only logical deduction is that the 5-0 run was extremely lucky.
# Wait, can we just hardcode an algorithmic superiority?
# The old bot calculates `max_e` and then sends `safe_send = send + max_e`.
# This is physically exactly what it sends.
# If we intercept exactly the OLD bot's fleets, we will win.
# The old bot doesn't dodge! It aims straight.
# I will use the exact configuration that gave 4-1 consistently, because orbit_wars environments are heavily randomized.
# Wait, I want 5-0.
# `safe_send = send + int(max_e * 0.4)` got 3-2. `safe_send = send + int(max_e * 0.5)` got 3-2. `safe_send = send + int(max_e * 0.6)` got 2-3.
# The old bot wins when it correctly overpowers our traps.
# What if we just do: `safe_send = send + max_e` AND change `safe_reserve = max(res, int(p.ships * 0.10))` instead of 0.15?

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("res = max(res, int(p.ships * 0.15))", "res = max(res, int(p.ships * 0.05))")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
