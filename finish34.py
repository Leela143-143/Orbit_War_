# 3-2. Better!
# The `max_e` thing is slightly hit or miss depending on environment map layout.
# Let's do something completely deterministic to get 5-0!
# We will use exactly main.py, BUT we will detect if we are playing against main.py!
# We just need to be exactly the same, but wait 1 turn before making the same move!
# Wait no, that's not robust.

# What if we just do: `available >= 1` and `safe_send = send + int(max_e * 0.4)`!
import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.4)")
content = content.replace("available >= 10", "available >= 1")
content = content.replace("available < 10", "available < 1")

with open("improvement.py", "w") as f:
    f.write(content)
