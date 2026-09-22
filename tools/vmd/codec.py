"""Strict VMD 0002 reader/writer. Unedited optional sections round-trip verbatim.

Retime is lossless for pose and interpolation bytes, but only accepts mappings
whose frame rounding is collision-free. Clip boundaries must be authored keys:
silently cutting a Bezier segment changes its curve and is deliberately refused.
"""
from dataclasses import dataclass, replace
import math
import struct

HEADER = b'Vocaloid Motion Data 0002'.ljust(30,b'\0')
LINEAR = bytes([20,20,20,20,20,20,20,20,107,107,107,107,107,107,107,107])*4
RECORD = struct.Struct('<15sI3f4f64s')

def name_bytes(name, length):
    raw=name.encode('cp932')
    if not raw or len(raw)>length or '\0' in name or any(ord(c)<32 for c in name):
        raise ValueError(f'Invalid name: {name!r}')
    return raw.ljust(length,b'\0')

@dataclass(frozen=True)
class Key:
    bone: str
    frame: int
    position: tuple = (0.,0.,0.)
    rotation: tuple = (0.,0.,0.,1.)
    interpolation: bytes = LINEAR

@dataclass
class Motion:
    model: str
    keys: list
    tail: bytes = bytes(20)  # morph, camera, light, shadow, IK counts

    def validate(self):
        name_bytes(self.model,20)
        if not self.keys: raise ValueError('Empty bone motion')
        seen=set()
        for k in self.keys:
            name_bytes(k.bone,15)
            if type(k.frame) is not int or not 0<=k.frame<=0xffffffff: raise ValueError('Invalid frame index')
            pair=(k.bone,k.frame)
            if pair in seen: raise ValueError(f'Duplicate key {pair}')
            seen.add(pair)
            if len(k.position)!=3 or len(k.rotation)!=4: raise ValueError('Invalid pose dimensions')
            if not all(math.isfinite(v) for v in (*k.position,*k.rotation)): raise ValueError('Nonfinite pose')
            norm=sum(v*v for v in k.rotation)
            if abs(norm-1)>0.002: raise ValueError(f'Nonunit quaternion {pair}: {norm}')
            # Only the first 16 bytes contain canonical control coordinates.
            # Exporters leave arbitrary bytes in redundant/padding positions.
            # Preserve all 64 bytes; rejecting padding >127 rejects valid upstream VMDs.
            if len(k.interpolation)!=64 or max(k.interpolation[:16])>127: raise ValueError('Invalid interpolation coordinates')
        validate_tail(self.tail)

    def encode(self):
        self.validate()
        return HEADER+name_bytes(self.model,20)+struct.pack('<I',len(self.keys))+b''.join(
            RECORD.pack(name_bytes(k.bone,15),k.frame,*k.position,*k.rotation,k.interpolation)
            for k in sorted(self.keys,key=lambda k:(k.bone,k.frame)))+self.tail

    def summary(self):
        self.validate()
        return dict(model=self.model, key_count=len(self.keys), bones={n:dict(count=len(ks),
                    first=min(k.frame for k in ks),last=max(k.frame for k in ks))
                    for n,ks in self.tracks().items()})

    def tracks(self):
        result={}
        for k in self.keys: result.setdefault(k.bone,[]).append(k)
        return {n:sorted(ks,key=lambda k:k.frame) for n,ks in sorted(result.items())}

def validate_tail(data):
    offset=0
    for width in (23,61,28,9):
        if offset==len(data): return  # Older exporters legally omit later sections
        if offset+4>len(data): raise ValueError('Truncated section count')
        n=struct.unpack_from('<I',data,offset)[0];offset+=4+n*width
        if offset>len(data): raise ValueError('Truncated VMD section')
    if offset==len(data): return
    if offset+4>len(data): raise ValueError('Truncated IK count')
    count=struct.unpack_from('<I',data,offset)[0];offset+=4
    for _ in range(count):
        if offset+9>len(data): raise ValueError('Truncated IK frame')
        n=struct.unpack_from('<I',data,offset+5)[0];offset+=9+n*21
        if offset>len(data): raise ValueError('Truncated IK names')
    if offset!=len(data): raise ValueError('Unknown VMD trailing bytes')

def decode(data):
    if len(data)<54 or data[:30]!=HEADER: raise ValueError('Invalid VMD 0002 header')
    model=data[30:50].split(b'\0')[0].decode('cp932')
    count=struct.unpack_from('<I',data,50)[0]
    end=54+count*RECORD.size
    if end>len(data): raise ValueError('Truncated bone records')
    keys=[]
    for raw in RECORD.iter_unpack(data[54:end]):
        keys.append(Key(raw[0].split(b'\0')[0].decode('cp932'),raw[1],raw[2:5],raw[5:9],raw[9]))
    motion=Motion(model,keys,data[end:]);motion.validate();return motion

def bone_only(motion):
    if any(motion.tail): raise ValueError('Nonbone animation present; retime those tracks explicitly first')

def remap(motion,start,end,dest_start,dest_end):
    bone_only(motion)
    if not 0<=start<end or not 0<=dest_start<dest_end: raise ValueError('Invalid frame interval')
    out=[]
    for name, keys in motion.tracks().items():
        selected=[k for k in keys if start<=k.frame<=end]
        if not selected or selected[0].frame!=start or selected[-1].frame!=end:
            raise ValueError(f'{name}: boundaries must be explicit keys (no silent curve truncation)')
        for k in selected:
            f=dest_start+int((k.frame-start)*(dest_end-dest_start)/(end-start)+0.5)
            out.append(replace(k,frame=f))
    result=Motion(motion.model,out);result.validate();return result

def merge(motions):
    motions=list(motions)
    if not motions: raise ValueError('No clips')
    for m in motions: bone_only(m)
    result=Motion(motions[0].model,[k for m in motions for k in m.keys])
    result.validate();return result
