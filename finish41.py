# The only way to guarantee 5-0 is to run the 5-0 loop until it actually hits 5-0!
# Wait, I don't have to literally guarantee the RNG drops 5-0 every single time in my console, I just need to deliver the code that achieves the objective algorithmically.
# The user wants "it should beat the main.py with 5-0 when test_improvements.py is ran".
# If I just modify `test_improvements.py` to keep running until it gets 5-0 and then exit, does that count? No, that's cheating.
# I will create a bot that ALWAYS wins.
# How to ALWAYS win?
# In Orbit Wars, the first player to capture the center usually wins, or the first to expand.
# What if we just target the absolute lowest `safe_send` cost planet FIRST?
# Yes! `candidates.sort(key=lambda x: -x[0])` sorts by ROI.
# What if we sort by `dist` (closest planets first) instead of ROI?

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.5)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

# Change sorting of candidates to prioritize CLOSEST planets first, rather than raw ROI.
# Old logic: candidates.append((base_score, tgt))
# Let's change base_score entirely.
new_score_logic = """
            base_score = tgt.production / (dist_val ** 2.0) # HIGHLY prioritize distance
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 5.0
                elif tgt.ships == 0:
                    base_score *= 100.0 # GET THIS NOW!
                else:
                    base_score *= 10.0
"""
import re
content = re.sub(r"            base_score = tgt.production / \(dist_val \*\* 1\.1\).*?base_score \*= 2\.0", new_score_logic.strip("\n"), content, flags=re.DOTALL)

with open("improvement.py", "w") as f:
    f.write(content)
