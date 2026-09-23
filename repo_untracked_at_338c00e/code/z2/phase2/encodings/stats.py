"""Extract comparable statistics from kissat -s / cadical logs in logs/."""
import re, sys, glob, os
def parse(path):
    txt = open(path, errors="replace").read()
    d = {"tag": os.path.basename(path)[:-4]}
    m = re.search(r"^s (\w+)", txt, re.M); d["result"] = m.group(1) if m else "?"
    def grab(key):
        m = re.search(r"^c %s:\s+([0-9.e+]+)" % key, txt, re.M); return float(m.group(1)) if m else None
    if "kissat" in txt[:2000] or "c ---- [ statistics ]" in txt or "c conflicts:" in txt and "kissat" in txt:
        pass
    for key, name in [("conflicts", "conflicts"), ("decisions", "decisions"), ("propagations", "propagations"),
                      ("learned", "learned"), ("learned_clauses", "learned"), ("literals_learned", "lits_learned"),
                      ("clauses_learned", "learned"), ("restarts", "restarts"), ("reductions", "reductions"),
                      ("chronological", "chrono"), ("backtracked", "backtracked"), ("trail", "trail")]:
        v = grab(key)
        if v is not None and name not in d: d[name] = v
    # cadical: "c conflicts:      12345   123.45  per second" ; "c learned: ... "; time: "c total process time since initialization: ... seconds"
    m = re.search(r"process time since initialization:\s+([0-9.]+)", txt); 
    if m: d["cpu"] = float(m.group(1))
    m = re.search(r"^c process-time:\s+([0-9.]+)", txt, re.M)
    if m: d["cpu"] = float(m.group(1))
    m = re.search(r"^c\s+([0-9.]+) seconds", txt, re.M)
    if m and "cpu" not in d: d["cpu"] = float(m.group(1))
    # kissat learned literals per clause: 'c literals_learned' / 'c learned'? try generic patterns
    m = re.search(r"^c learned:\s+([0-9]+)\s+([0-9.]+)\s+per conflict", txt, re.M)  # cadical
    m2 = re.search(r"^c learned:\s+([0-9]+)\s+clauses\s+([0-9.]+)\s+per conflict", txt, re.M)
    m3 = re.search(r"^c\s+learned_clauses:\s+([0-9]+)", txt, re.M)
    if m3: d["learned"] = float(m3.group(1))
    # size of learned clauses (kissat): 'c learned_literals'? try
    m = re.search(r"^c\s+literals_learned:\s+([0-9]+)", txt, re.M)
    if m: d["lits_learned"] = float(m.group(1))
    m = re.search(r"^c literals_learned:\s+([0-9]+)", txt, re.M)
    if m: d["lits_learned"] = float(m.group(1))
    m = re.search(r"^c\s+trail_(?:height|max)\S*:?\s+([0-9.]+)", txt, re.M)
    return d, txt
if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob("logs/*.log"))
    for f in files:
        d, txt = parse(f)
        cpu = d.get("cpu") or 1.0
        line = "%-28s %-8s cpu=%7.1f" % (d["tag"], d["result"], cpu)
        for k in ("conflicts", "decisions", "propagations", "learned", "restarts"):
            if k in d: line += " %s=%.3g(%.3g/s)" % (k, d[k], d[k] / cpu)
        if "lits_learned" in d and d.get("learned"): line += " avg_learned_len=%.1f" % (d["lits_learned"] / d["learned"])
        print(line)
