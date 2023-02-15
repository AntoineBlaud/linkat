
import subprocess
from collections import Counter


def echo(msg, filename):
    subprocess.call(f"echo {msg} >> {filename}", shell=True)
    
def clear(filename):
    subprocess.call(f"echo -n > {filename}", shell=True)
    
    
def count_events(events, key):
    return Counter(event[key] for event in events)