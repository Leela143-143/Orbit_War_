# Still struggling!
# Let me implement the SINGLE MOST POWERFUL heuristic I've found so far:
# 1. Expand to `tgt.ships == 0` aggressively!
# 2. `safe_send = send + int(max_e * 0.5)`
# 3. `available >= 5`
# 4. If we STILL lose, it's just pure map randomness and the bot is functionally identical to the 4-1 run.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

new_score_logic = """
            base_score = tgt.production / (dist_val ** 0.8) # distance matters even less!
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 10.0
                elif tgt.ships == 0:
                    base_score *= 100.0 # MEGA GET THIS NOW!
                else:
                    base_score *= 5.0 # Expand way more aggressively
"""

import re
content = re.sub(r"            base_score = tgt.production / \(dist_val \*\* 1\.1\).*?base_score \*= 2\.0", new_score_logic.strip("\n"), content, flags=re.DOTALL)

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.5)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
