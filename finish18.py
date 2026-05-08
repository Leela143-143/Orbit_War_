# In `fix_timing21.py`, I wrote the ultimate 5-0 algorithmic counter!
# Let me look closely at `fix_timing21.py`.
# Wait, `fix_timing21.py` actually won 1 game and OLD bot won 4 games!
# It was `fix_timing12.py` that won 5-0!

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.5)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
