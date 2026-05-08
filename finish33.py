# 4-1 for old! Wow.
# So max_e needs to be low enough so we actually attack.
# Let's try max_e * 0.45 and available >= 2.
import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.45)")
content = content.replace("available >= 10", "available >= 2")
content = content.replace("available < 10", "available < 2")

with open("improvement.py", "w") as f:
    f.write(content)
