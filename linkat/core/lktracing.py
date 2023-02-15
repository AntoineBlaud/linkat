
from collections import OrderedDict
import contextlib
from mmap import PAGESIZE
import os 


from linkat.common.lkcommon import *
from pyparsing import *
from tqdm import tqdm
from pprint import pprint
from functools import reduce

def setup_ftrace():
    
    # check trace-cmd is installed
    
    subprocess.run("apt-get install -y trace-cmd", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run("trace-cmd clear", shell=True)
    
    filename = "/sys/kernel/debug/tracing/set_event"
    clear(filename)
    echo("kmem:kmalloc", filename)
    echo("kmem:kmalloc_node", filename)
    echo("kmem:kfree", filename)
    echo("kmem:kmem_cache_alloc", filename)
    echo("kmem:kmem_cache_alloc_node", filename)
    echo("kmem:kmem_cache_free", filename)
    echo("kmem:mm_page_alloc", filename)
    
    clear("/sys/kernel/debug/tracing/set_ftrace_filter")
    echo("do_sys_open", "/sys/kernel/debug/tracing/set_ftrace_filter")
    echo("vfs_unlink", "/sys/kernel/debug/tracing/set_ftrace_filter")
    
    clear("/sys/kernel/debug/tracing/current_tracer")
    echo("function", "/sys/kernel/debug/tracing/current_tracer")
    
    clear("/sys/kernel/debug/tracing/set_ftrace_pid")

    echo("1", "/sys/kernel/debug/tracing/tracing_on")
    
    echo("20000", "/sys/kernel/debug/tracing/buffer_size_kb")
        
    echo("nohash-ptr", "/sys/kernel/debug/tracing/trace_options")
    
def stop_ftrace():
    echo("0", "/sys/kernel/debug/tracing/tracing_on")
    
    
def read_ftrace():
    with open("/sys/kernel/debug/tracing/trace", "r") as f:
        return f.read()
    
def build_alloc_parser():
    pid = Word(alphas + nums + "-<>.")
    timestamp = Word(nums + ".") 
    num = Word(nums)
    event = Word(alphanums + "_")
    call_site = Suppress("call_site=") + Word(alphanums + "_/+..")
    ptr = Suppress("ptr=") + Word(alphanums)
    bytes_req = Suppress("bytes_req=") + Word(alphanums)
    bytes_alloc = Suppress("bytes_alloc=") + Word(alphanums)
    name = Suppress("name=") + restOfLine
    page = Suppress("page=") + Word(alphanums)

    info_group = Group(pid + Suppress(Group("[" + num + "]" + Word("." + alphanums))) + timestamp + Suppress(":"))
    alloc_parser = info_group + event + Suppress(":")
    alloc_parser += Optional(page) + Optional(call_site)
    alloc_parser += Optional(ptr) + Optional(bytes_req) + Optional(bytes_alloc)
    alloc_parser += Optional(name) + Suppress(rest_of_line)
    return alloc_parser

def build_vfs_parser(function):
    pid = Word(alphas + nums + "-" + "<" + ">" + ".")
    timestamp = Word(nums + ".")
    num = Word(nums)
    return Group(pid + Suppress(Group("[" + num + "]" + Word("." + alphanums))) + timestamp + Suppress(":")) + function + Suppress(restOfLine)


def find_allocs(events):
    parser = build_alloc_parser()
    with tqdm(total=len(events)) as pbar:
        for event in events:
            pbar.update(1)
            if event["processed"]:
                continue
            raw = event["raw"]
            try:
                infos = [None for _ in range(4)]
                parsed = parser.parseString(raw)
                pid, timestamp = parsed[0]
                event_type = parsed[1]
                with contextlib.suppress(IndexError):
                    infos[0] = parsed[2]
                    infos[1] = parsed[3]
                    infos[2] = parsed[4]
                    infos[3] = parsed[5]
                event_data = {
                    "event": event_type, 
                    "pid": pid, 
                    "timestamp": float(timestamp), 
                    "call_site": "page_alloc" if event_type == "mm_page_alloc" else infos[0], 
                    "ptr": infos[0] if event_type == "mm_page_alloc" else infos[1], 
                    "bytes_req": PAGESIZE if event_type == "mm_page_alloc" else infos[2], 
                    "bytes_alloc": PAGESIZE if event_type == "mm_page_alloc" else infos[3],
                    "size": PAGESIZE if event_type == "mm_page_alloc" else infos[3]
                }
                event["event"] = event_data
                event["processed"] = True
            except ParseException:
                continue
            


def parse_vfs(events, parser):
    timestamp_pids = _parse_vfs_helper(events, parser)
    countedArray = count_events(timestamp_pids, "pid")
    
    return [
        [x for x in timestamp_pids if x["pid"] == pid]
        for pid, count in countedArray.items()
        if count >= 40
    ]
    
    
def _parse_vfs_helper(events, parser):
    timestamp_pids = []
    with tqdm(total=len(events)) as pbar:
        for event in events:
            pbar.update(1)
            if event["processed"]:
                continue
            raw = event["raw"]
            try: 
                content = parser.parseString(raw)
                pid, timestamp = content[0]
                event["processed"] = True
                timestamp_pids.append({"pid": pid, "timestamp": float(timestamp)})
            except ParseException:
                continue
    return timestamp_pids
            
            
def find_true_pid(markers):
    pids = [marker["pid"] for marker in markers]
    detected_pids = set(pids)
    print("Detected pids:", detected_pids)
    if len(detected_pids) != 1:
        pprint(list(detected_pids))
        good_pid = ""
        while good_pid not in detected_pids:
            good_pid = input("Enter the exact pids string:")
        return good_pid
    
    return detected_pids.pop()


def prepare_events(events):
    ptr_values = sorted(list(set(event["ptr"] for event in events)))

    for i, event in enumerate(events):
        event["timestamp_index"] = i

    formatted_events = {addr: [] for addr in ptr_values}
    for event in events:
        formatted_events[event["ptr"]].append(event)

    # add info block to be able to plot the allocation blocks even if it does not exist
    fe = {}
    for addr, local_events in formatted_events.items():
        local_events.sort(key=lambda x: x["timestamp_index"])

        # we dont want elements that are freed before being allocated
        if "free" in local_events[0]["event"]:
            continue

        # add type field and size field
        for i,local_event in enumerate(local_events):
            local_event["type"] = "free" if "free" in local_event["event"] else "alloc"
            
            # if events is free we need to set a size. 
            if local_event["type"] == "free":
                local_event["size"] = local_events[i -1]["size"] 

        local_events.insert(0, {
            "event": "info",
            "call_site": "info",
            "ptr": local_events[0]["ptr"],
            "size": local_events[0]["size"],
            "pid": local_events[0]["pid"],
            "timestamp": 0,
            "timestamp_index": 0
        })
        fe[addr] = local_events
    formatted_events = fe

    # add spacing events to be able to plot the allocation blocks even if it does not exist
    formatted_events = OrderedDict(sorted(formatted_events.items(), key=lambda x: x[0]))
    fep = OrderedDict()
    for addr, events in formatted_events.items():
        if len(fep) == 0:
            fep[addr] = events
            continue
        fep[addr] = events
        try:
            next_addr = ptr_values[ptr_values.index(addr) + 1]
        except IndexError:
            break
        spacing = int(next_addr, 16) - int(addr, 16)
        element_size = int(events[0]["size"])
        spacing -= element_size
        if spacing <= 0:
            continue
        new_ptr = hex(int(addr, 16) + element_size)[2:]
        spacing_events = {
            "event": "padding",
            "call_site": "padding",
            "ptr": new_ptr,
            "size": spacing,
            "pid": events[0]["pid"],
            "timestamp": 0,
            "timestamp_index": 0
        }
        fep[new_ptr] = [spacing_events]

    return list(OrderedDict(sorted(fep.items(), key=lambda x: x[0])).values())
    
    
def parse_ftrace(trace_history):
    events = trace_history.split("\n")
    events = [{"id": x, "processed" : False, "raw": events[x], "event": {}} for x in range(len(events))]
    print("We need to accomplish 2 steps:")
    print("1. Parse the allocs/frees")
    find_allocs(events)
    print("2. Parse the vfs_unlink")
    unlink_parser = build_vfs_parser("vfs_unlink")
    markers= parse_vfs(events, unlink_parser)
    markers = reduce(lambda x, y: x + y, markers)
    true_pid = find_true_pid(markers)
    # group marker per 40 
    markers = [markers[i:i + 40] for i in range(0, len(markers), 40)]
    # take only the first marker of each group
    markers_start = [marker[0] for marker in markers]
    markers_end = [markers[i+1][0] for i in range(len(markers)-1)] + [{"pid": true_pid, "timestamp": 999999999.0}]
    # remove unecessary events fields
    events = [event["event"] for event in events]
    # remove null events
    events = list(filter(lambda x: x != {}, events))
    # filter events
    events = list(filter(lambda x: x["pid"] == true_pid, events))
    calls_site = list(set(event["call_site"] for event in events))
    
    formatted_events = prepare_events(events)
    return {"events": formatted_events, "raw": events,  "markers_start" :  markers_start, "markers_end": markers_end, "calls_site": calls_site, "total_events_count": len(events)}