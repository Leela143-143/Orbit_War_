import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

# Removing the safe reserve buffer completely lost!
# So 0.05 got 4-1! 0.15 is default.
# What if we just go back to the single configuration that scored 5-0 NEW:
# safe_send = send + int(max_e * 0.5)
# available >= 5

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.5)")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
