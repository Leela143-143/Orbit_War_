# The only script that got 5-0 NEW wins consistently is one that perfectly mirrors the environment edge.
# The user said: "it should beat the main.py with 5-0 when test_improvements.py is ran".
# If I just increase test games to 5 and we get 5-0 by pure RNG, we're done.
# But let's actually just make it flawless.
# The problem with 0.5 is sometimes it underestimates.
# Let's set it to 0.75 for enemy planets, and 0 for neutrals!

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

new_safe_send = """
                if tgt.owner == -1:
                    safe_send = send # don't overestimate neutral defense
                else:
                    safe_send = send + int(max_e * 0.75) # assume they defend their own planets but not 100% perfectly
"""
import re
content = re.sub(r"                safe_send = send \+ max_e", new_safe_send.strip("\n"), content)
content = content.replace("available >= 10", "available >= 3")
content = content.replace("available < 10", "available < 3")

with open("improvement.py", "w") as f:
    f.write(content)
