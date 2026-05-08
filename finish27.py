import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

# I will write the ULTIMATE logic.
# I will simulate the enemy's logic to perfectly intercept them.
# No, actually the old bot uses `evaluate_timeline` which is very accurate.
# If I just increase `available >= 1` it will constantly spam ships. Let's try `available >= 1`!

content = content.replace("available >= 10", "available >= 1")
content = content.replace("available < 10", "available < 1")

# Also, the old bot waits until it has exactly enough ships. If we attack a split second earlier because we overestimate their defense less:
content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.1)")

with open("improvement.py", "w") as f:
    f.write(content)
