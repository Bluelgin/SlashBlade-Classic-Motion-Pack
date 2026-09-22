import argparse
import json
from pathlib import Path
from .codec import decode, remap, merge

ap=argparse.ArgumentParser(description='Inspect, validate, extract, retime and merge VMD bone clips')
sub=ap.add_subparsers(dest='cmd',required=True)
for cmd in ('inspect','validate'):
    p=sub.add_parser(cmd);p.add_argument('file',type=Path)
p=sub.add_parser('remap');p.add_argument('file',type=Path);p.add_argument('output',type=Path)
for n in ('start','end','dest_start','dest_end'):p.add_argument(n,type=int)
p=sub.add_parser('merge');p.add_argument('output',type=Path);p.add_argument('files',type=Path,nargs='+')
a=ap.parse_args()
if a.cmd=='merge': a.output.write_bytes(merge(decode(f.read_bytes()) for f in a.files).encode())
else:
    m=decode(a.file.read_bytes())
    if a.cmd=='remap':a.output.write_bytes(remap(m,a.start,a.end,a.dest_start,a.dest_end).encode())
    else:print(json.dumps(m.summary(),indent=2,ensure_ascii=False))
