# 4-1! It's SO CLOSE.
# The `fix_timing24.py` script literally did EXACTLY this and got 5-0.
# The environment randomness is causing 4-1 sometimes.
# Is there anything else? Let's reduce `safe_send = send + int(max_e * 0.45)`.
import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.45)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
