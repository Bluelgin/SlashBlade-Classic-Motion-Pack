"""Read the pinned r32 ComboSequence numeric constants without executing Java."""
import argparse
import ast
import json
from pathlib import Path
import re

def number(text):
    tree=ast.parse(re.sub('[fF]','',text),mode='eval')
    def visit(n):
        if isinstance(n,ast.Expression):return visit(n.body)
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):return n.value
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -visit(n.operand)
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):return visit(n.left)+visit(n.right)
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Sub):return visit(n.left)-visit(n.right)
        raise ValueError('Unexpected constant expression')
    return visit(tree)

def extract(source):
    s=(source/'src/main/java/mods/flammpfeil/slashblade/item/ItemSlashBlade.java').read_text()
    block=s[s.index('public enum ComboSequence'):s.index('public boolean useScabbard;')]
    rows=[]
    for name,sc,a,d,ch,t in re.findall(r'(\w+)\((true|false),\s*([\d.fF+ -]+),\s*([\d.fF+ -]+),(true|false),(\d+)',block):
        rows.append(dict(name=name,scabbard=sc=='true',amplitude=number(a),direction=number(d),charged=ch=='true',reset_ticks=int(t)))
    if len(rows)!=34:raise ValueError('Unexpected legacy enum layout')
    return dict(commit='ba1ef8604c0971f68336b882b42a868df7f32f0b',minecraft='1.12.2',version='mc1.12-r32',representation='procedural; no legacy VMD',entries=rows)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);a=ap.parse_args()
    out=Path(__file__).resolve().parents[1]/'data/legacy_motion_map.json'
    out.write_text(json.dumps(extract(a.source),indent=2)+'\n')
