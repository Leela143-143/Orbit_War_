# The 5-0 was likely heavily dependent on random seeds.
# Let's add a massive tie-breaker advantage to make sure we always win the marginal engagements.
# We will use exactly this configuration, but we will send exactly +1 extra ship compared to what the old bot sends!
# The old bot calculates `max_e`. We calculate `max_e * 0.5`. This causes us to send LESS ships and sometimes lose.
# Let's send `max_e + 2` to ALWAYS win!
# And change `available >= 1` to always attack!
# No, micro-fleets are good: `available >= 5` is great.
# Let's do `safe_send = send + max_e + 3` to out-muscle the old bot.

import shutil
shutil.copy("main.py", "improvement.py")

with open("improvement.py", "r") as f:
    content = f.read()

content = content.replace("safe_send = send + max_e", "safe_send = send + max_e + 5")
content = content.replace("available >= 10", "available >= 5")
content = content.replace("available < 10", "available < 5")

with open("improvement.py", "w") as f:
    f.write(content)
