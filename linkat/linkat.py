

from linkat.core.lktracing import *
from linkat.core.legends import *
import os 
from flask_cors import CORS
from flask import Flask, request, jsonify
import json 
import argparse

def main():
    
    arg = argparse.ArgumentParser()
    arg.add_argument("-f", "--file", help="Path to the events parsed file", required=False)
    args = arg.parse_args()
    
    if args.file:
        trace = json.load(open(args.file, "r"))
        
    else :
        # check we are root
        if os.geteuid() != 0:
            raise RuntimeError("You need to be root to run this script")
        
        
        setup_ftrace()
        input("Press 'Enter' when your done...")
        trace_history = read_ftrace()
        stop_ftrace()
        trace  = parse_ftrace(trace_history)
        print("[+] Done parsing ftrace")
        trace["legends"] = build_legends(trace)
        json.dump(trace, open("trace.json", "w"))
        print("[+] Done. Trace saved to trace.json")
        
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/events')
    def events():
        return {"events": trace["events"]}
    
    @app.route('/api/markers')
    def markers():
        return {"markers_start": trace["markers_start"], "markers_end": trace["markers_end"]}
    
    @app.route('/api/legends')
    def legends():
        return {"legends": trace["legends"]}
    
    @app.route('/api/events/size')
    def events_sizes():
        return {"size": trace["total_events_count"]}
    
    
    
    app.run(debug=False, host="0.0.0.0", port=5000)
    
    
    
if __name__ == '__main__':
    main()