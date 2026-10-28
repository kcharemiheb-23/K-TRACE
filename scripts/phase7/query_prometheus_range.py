#!/usr/bin/env python3
import argparse
import json
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--query", required=True)
parser.add_argument("--start", required=True)
parser.add_argument("--end", required=True)
parser.add_argument("--step", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

params = urllib.parse.urlencode({
    "query": args.query,
    "start": args.start,
    "end": args.end,
    "step": args.step,
})
url = f"http://127.0.0.1:9090/api/v1/query_range?{params}"

with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode("utf-8"))

with open(args.out, "w") as f:
    json.dump(data, f)
