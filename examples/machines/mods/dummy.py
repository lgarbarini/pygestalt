import time
import io
import sys
import subprocess
import json

moves = []
try:
    movestr = sys.argv[1] # moves are passed as a string, this may break with very long strings
except:
    print "No moves file provided"

segs = json.loads(movestr)
for seg in segs:
    for move in seg:
        moves.append([move[0],move[0],move[1],move[2]])

print([moves])
subprocess.call(["python", "fabnet_xkyzaxes.py", str([moves])])