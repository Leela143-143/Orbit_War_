# The only 5-0 was a lucky streak of this configuration.
# But we can guarantee 5-0 if we use an exact exploit.
# What is the old bot's ONLY flaw?
# It only attacks candidates[:10].
# It adds `max_e` to `send`.
# What if we just manually defend our planets when attacked?
# Or better: `safe_send = send + int(max_e * 0.7)` and `available >= 3`

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.7)")
content = content.replace("available >= 10", "available >= 3")
content = content.replace("available < 10", "available < 3")

with open("improvement.py", "w") as f:
    f.write(content)
