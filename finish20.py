# Okay, `0.75` for enemy planets and `0` for neutrals got crushed.
# The only configuration that consistently wins the MOST is:
# safe_send = send + int(max_e * 0.5)
# Let's restore the 5-0 configuration exactly again and just submit it because we got 5-0 on it once and 4-1 consistently.
# Wait, I also had a 5-0 on `fix_timing12.py` which was:
# safe_send = send + int(max_e * 0.5)
# available >= 5
# NO SCORE LOGIC CHANGE.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.5)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
