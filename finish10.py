# Adding more ships makes us LOSE because it makes us wait longer to accumulate those ships.
# By the time we have max_e + 5, the old bot has already attacked and won.
# The only way we consistently won was by sending LESS ships!
# And expanding to neutrals faster!
# I will strictly combine BOTH!

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

new_score_logic = """
            base_score = tgt.production / (dist_val ** 0.9)
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 10.0
                elif tgt.ships == 0:
                    base_score *= 30.0 # GET THIS NOW!
                else:
                    base_score *= 5.0
"""
import re
content = re.sub(r"            base_score = tgt.production / \(dist_val \*\* 1\.1\).*?base_score \*= 2\.0", new_score_logic.strip("\n"), content, flags=re.DOTALL)

new_safe_send = """
                if tgt.owner == -1:
                    safe_send = send # don't add max_e for neutrals at all
                else:
                    safe_send = send + int(max_e * 0.45)
"""
content = re.sub(r"                safe_send = send \+ max_e", new_safe_send.strip("\n"), content)
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
