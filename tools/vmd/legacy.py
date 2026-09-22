"""Offline sampling of r32 LayerSlashBlade's procedural blade/saya transforms.

Source and terms: docs/research/legacy-1.12.2-source.md and THIRD_PARTY_NOTICES.md.
Not an invented skeletal animation. No upstream models/textures are copied.
"""
from .transforms import chain, identity, translation as T, rotate as R, scale as S, quaternion

def progress(t, name):
    p=max(0.,min(1.,t*1.2))
    if name in ('Iai','SIai'):return 1-abs(p-.5)*2
    if name in ('Stinger','HiraTuki'):return 1.
    return 1-(1-p)**2

def dynamic(combo,t,sheath=False):
    name=combo['name'];amp=combo['amplitude'];direction=combo['direction']
    if name=='None' or (sheath and not combo['scabbard']):return identity()
    p=progress(t,name)
    if amp<0:p=1-p
    pre=T(0,0,-26) if name in ('Stinger','HiraTuki') and not sheath else identity()
    if name=='Kiriorosi' and not sheath:
        return chain(pre,R('x',-20),R('z',30),T(0,0,-8),R('y',-(90-direction)),
            R('z',(1-p)*90),T((1-p)*10,(1-p)*-5,0),T(-10,-8,0),
            R('z',-abs(amp)),T(10,8,0),R('y',180))
    if direction<0 and not sheath:
        return chain(pre,R('x',-20),R('z',30),T(0,0,-12),R('y',-(90+direction)),
            R('z',(1-p)*240),T(-10,-8,0),R('z',-p*abs(amp)),T(10,8,0))
    return chain(pre,R('x',-20*p),R('z',30*p),R('y',-p*(90-direction)),
                 T(-10,-8,0),R('z',-p*abs(amp)),T(10,8,0))

def legacy_world(combo,t,sheath=False):
    # Same relative render-layer coordinates as the modern layer (standing adult).
    return chain(T(.25,.4,-.5),S(.075),R('x',60),R('z',-20),R('y',90),
                 dynamic(combo,t,sheath),S(1/.075),R('z',-90))

def pose(combo,t,sheath=False):
    # Modern: T(0,1.5,0) S(.125) Rz(180) Sx(-1) M Sx(-1).
    # Invert the prefix, preserving blade-holder zero bind positions.
    m=chain(S(-1,1,1),R('z',-180),S(8),T(0,-1.5,0),
            legacy_world(combo,t,sheath),S(.125),S(-1,1,1))
    # Uniform scale cancels only in rotation; translation remains in PMD units.
    return tuple(m[i][3] for i in range(3)),quaternion(m)
