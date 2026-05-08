# 4-1! `available >= 1` works well.
# What if we just reduce `max_e` slightly more? `0.3`?

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.3)")
content = content.replace("available >= 10", "available >= 1")
content = content.replace("available < 10", "available < 1")

with open("improvement.py", "w") as f:
    f.write(content)
