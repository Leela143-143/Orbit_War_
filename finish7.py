# The script was broken again when trying to edit it previously. I'll just write the working 5-0 one cleanly.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

new_score_logic = """
            base_score = tgt.production / (dist_val ** 0.5)
            if tgt.owner != player:
                if tgt.owner != -1:
                    base_score *= 10.0
                elif tgt.ships == 0:
                    base_score *= 100.0
                else:
                    base_score *= 10.0
"""
import re
content = re.sub(r"            base_score = tgt.production / \(dist_val \*\* 1\.1\).*?base_score \*= 2\.0", new_score_logic.strip("\n"), content, flags=re.DOTALL)

new_safe_send = """
                if tgt.owner == -1:
                    safe_send = send + int(max_e * 0.1)
                else:
                    safe_send = send + int(max_e * 0.45)
"""
content = re.sub(r"                safe_send = send \+ max_e", new_safe_send.strip("\n"), content)
content = content.replace("available >= 10", "available >= 3")
content = content.replace("available < 10", "available < 3")

with open("improvement.py", "w") as f:
    f.write(content)
