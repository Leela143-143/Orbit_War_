# If 4-1 is the limit due to map RNG, I will add ONE final safeguard to get 5-0.
# The OLD bot's only real advantage when we lose is that it correctly overpowers OUR defenses.
# If we simply multiply `max_e` by `0.6` instead of `0.5`, maybe it defends better.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.6)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
