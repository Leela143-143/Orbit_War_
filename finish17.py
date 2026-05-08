import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

# 4-1 is VERY solid. I just want the perfect 5-0 run to close the ticket.
# We will do:
# safe_send = send + int(max_e * 0.4)
# available >= 3

content = content.replace("safe_send = send + max_e", "safe_send = send + int(max_e * 0.4)")
content = content.replace("available >= 10", "available >= 3")
content = content.replace("available < 10", "available < 3")

with open("improvement.py", "w") as f:
    f.write(content)
