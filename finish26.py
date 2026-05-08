import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

# I am returning to the single run that achieved 5-0 (which I got from fix_timing12.py but lost later due to randomness).
# The prompt ONLY asks to beat the bot. I will write a simple fix that creates a dominant bot.

new_score_logic = """
            base_score = tgt.production / (dist_val ** 0.8) # distance matters even less!
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 10.0
                elif tgt.ships == 0:
                    base_score *= 20.0 # GET THIS NOW!
                else:
                    base_score *= 5.0 # Expand way more aggressively
"""

import re
content = re.sub(r"            base_score = tgt.production / \(dist_val \*\* 1\.1\).*?base_score \*= 2\.0", new_score_logic.strip("\n"), content, flags=re.DOTALL)

new_safe_send = """
                if tgt.owner == -1:
                    safe_send = send + int(max_e * 0.2)
                else:
                    safe_send = send + int(max_e * 0.5)
"""
content = re.sub(r"                safe_send = send \+ max_e", new_safe_send.strip("\n"), content)
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
