# 4-1 ! We got 4-1 just by changing safe_reserve from 0.15 to 0.05 and available from 10 to 5.
# Let's change safe_reserve to 0.0, because safe_reserve already calculates exactly what we need using simulated planet arrivals!
# The `max(res, int(p.ships * 0.15))` is an artificial buffer. If we remove it, we expand perfectly efficiently.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("res = max(res, int(p.ships * 0.15))", "res = res")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
