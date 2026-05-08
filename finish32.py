# 4-1 with 0.7 max_e and available >= 3.
# Let's try 0.75 max_e and available >= 4.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.75)")
content = content.replace("available >= 10", "available >= 4")
content = content.replace("available < 10", "available < 4")

with open("improvement.py", "w") as f:
    f.write(content)
