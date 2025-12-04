import subprocess

with open('requirements.txt', 'r') as f:
    lines = f.readlines()

for line in lines:
    package = line.strip()
    if package:
        if "airsim" not in package:
            subprocess.run(['pip', 'install', package])

for line in lines:
    package = line.strip()
    if package:
        subprocess.run(['pip', 'install', package])