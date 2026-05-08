# The only stable path is to be slightly more patient to avoid throwing away ships,
# but still more aggressive than OLD bot.
# OLD bot: available >= 10, max_e = 1.0.
# We will do: available >= 8, max_e = 0.8.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.8)")
content = content.replace("available >= 10", "available >= 8")
content = content.replace("available < 10", "available < 8")

with open("improvement.py", "w") as f:
    f.write(content)
