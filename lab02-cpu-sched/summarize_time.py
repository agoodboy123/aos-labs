#!/usr/bin/env python3
import glob, re, csv

patterns = {
    "user_sec":  r"User time \(seconds\):\s*([0-9.]+)",
    "sys_sec":   r"System time \(seconds\):\s*([0-9.]+)",
    "cpu_pct":   r"Percent of CPU this job got:\s*([0-9]+)%",
    "vol_cs":    r"Voluntary context switches:\s*([0-9]+)",
    "invol_cs":  r"Involuntary context switches:\s*([0-9]+)",
    "elapsed_raw": r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*([0-9:.]+)",
}

def elapsed_to_sec(s):
    s = s.strip()
    parts = s.split(":")
    try:
        if len(parts) == 3:
            h, m, sec = parts
            return int(h) * 3600 + int(m) * 60 + float(sec)
        if len(parts) == 2:
            m, sec = parts
            return int(m) * 60 + float(sec)
        return float(s)
    except Exception:
        return ""

rows = []
for path in sorted(glob.glob("logs/*.time")):
    text = open(path, errors="ignore").read()
    row = {"file": path}
    for k, pat in patterns.items():
        m = re.search(pat, text)
        row[k] = m.group(1) if m else ""
    row["elapsed_sec"] = elapsed_to_sec(row.get("elapsed_raw", ""))
    rows.append(row)

if rows:
    keys = ["file", "elapsed_sec", "user_sec", "sys_sec", "cpu_pct", "vol_cs", "invol_cs"]
    with open("logs/summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Generated logs/summary.csv")
    print("Total records: {}".format(len(rows)))
else:
    print("No .time files found in logs/")
