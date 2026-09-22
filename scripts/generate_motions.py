"""Generate resource-only experimental motion set, without third-party binaries."""
import argparse
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.vmd.codec import Motion, Key, name_bytes
from tools.vmd.legacy import pose
from tools.vmd.transforms import slerp

ROOT=Path(__file__).resolve().parents[1]
VMD_FPS=30
GAME_TPS=20
VANILLA_SWING_FRAMES=9
NOUTOU_ENTRY_DELAY_TICKS=5
DIRECT_NONE_MOVES={'SlashDim','Iai','SIai','Noutou'}
ADAPTATION_CLASSES={'CLASSIC_RESTORATION','CLASSIC_INTERPRETATION'}
PIERCING_ACTIVE_FRAME=33
PIERCING_MAX_FRAME=90

def mix(a,b,t):
    return tuple(x+(y-x)*t for x,y in zip(a[0],b[0])),slerp(a[1],b[1],t)

def legacy_reset_frames(combo,entry_delay_ticks=0):
    """Convert r32 comboResetTicks (+ an optional entry clock offset) to VMD frames."""
    return round((combo['reset_ticks']+entry_delay_ticks)*VMD_FPS/GAME_TPS)

def noutou_state_frames(combos):
    """Visible r32 Noutou lifetime after a normal blade timeout.

    r32 does not merely play one six-tick swing and immediately become None.
    The transition into Noutou stores LastActionTime=currentTime+5, then Noutou's
    own five-tick reset clock runs.  The swing reaches its final pose after six
    ticks and that pose is held until the delayed Noutou state actually expires.
    We use the server-side source clock here, matching the other legacy-reset
    conversions in this baker.
    """
    frames=legacy_reset_frames(combos['Noutou'],NOUTOU_ENTRY_DELAY_TICKS)
    return max(VANILLA_SWING_FRAMES,frames)

def last_legacy_move(slot):
    if slot.get('segments'):
        segment=slot['segments'][-1]
        return segment['legacy'],segment['start']
    if 'second_legacy' in slot:
        return slot['second_legacy'],slot['second_start']
    return slot['legacy'],slot['start']+slot.get('attack_offset',0)

def resolve_recovery(slot,combos):
    """Resolve the first recovery frame, optionally from the pinned r32 reset clock.

    Embedded multi-move slots use their final legacy move as the recovery clock
    origin. The resolved reset is clamped to the modern atlas window because a
    resource pack cannot keep controlling a state after Resharped leaves it.
    `legacy_entry_delay_ticks` models source-side clock offsets such as r32's
    `LastActionTime = currentTime + 5` when entering Noutou.
    """
    if slot.get('recovery_mode')!='legacy_reset':
        return slot['recovery_start']
    name,origin=last_legacy_move(slot)
    entry_delay=slot.get('legacy_entry_delay_ticks',0)
    resolved=min(slot['end'],origin+legacy_reset_frames(combos[name],entry_delay))
    declared=slot.get('recovery_start')
    if declared is not None and declared!=resolved:
        raise ValueError(f"{slot['name']} recovery_start={declared}, expected legacy reset {resolved}")
    return resolved

def timeout_target(slot,combos):
    """Return the r32 visual state entered after the final mapped move times out.

    In ItemSlashBlade.onUpdate, saya moves, SlashDim/Iai/SIai and Noutou reset
    straight to None. Other non-saya moves enter Noutou and restart the vanilla
    swing. The mapped moves used by this pack do not rely on a scabbard
    mainHandCombo.
    """
    name,_=last_legacy_move(slot)
    combo=combos[name]
    if combo['scabbard'] or name in DIRECT_NONE_MOVES:
        return 'none'
    return 'noutou'

def noutou_recovery_pose(frame,recovery,combos,sheath):
    """Pose the delayed r32 Noutou state entered after a blade move times out."""
    elapsed=frame-recovery
    if elapsed<VANILLA_SWING_FRAMES:
        return pose(combos['Noutou'],elapsed/VANILLA_SWING_FRAMES,sheath)
    if elapsed<noutou_state_frames(combos):
        return pose(combos['Noutou'],1,sheath)
    return pose(combos['None'],0,sheath)

def passthrough_pmd():
    # Bone-only PMD, no borrowed mesh. Unknown body-part names cause the existing
    # VmdAnimation adapter to return value0; vanilla poses are not zeroed out.
    b=b'Pmd'+struct.pack('<f',1)+name_bytes('Classic passthrough',20)
    b+=b'Original bone-only rig; preserve vanilla player transforms.'.ljust(256,b'\0')
    b+=struct.pack('<IIIH',0,0,0,1)  # vertices, indices, materials, bones
    b+=struct.pack('<20sHHBH3f',name_bytes('classic_root',20),65535,0,1,0,0,0,0)
    b+=struct.pack('<HHBBIB',0,0,0,0,0,0)  # IK, morphs, displays, English flag
    b+=bytes(1000)+struct.pack('<II',0,0)  # toon names, rigid bodies, joints
    return b

def classic_piercing_motions(combos):
    """Build the dedicated modern Piercing atlas as a classic interpretation.

    Resharped uses an isolated 1..90 VMD for Piercing. Frames 1..32 are its
    preparation/hold state. At frame 33 the Java combo begins the actual forward
    lunge and area hit. r32's Stinger is the closest classic semantic match and
    intentionally evaluates at full thrust progress; its 20-tick reset clock is
    preserved on the 30 Hz atlas, so recovery begins at frame 63. Non-saya r32
    moves then enter the delayed Noutou state: a fresh six-tick swing reaches the
    final pose, which remains held until the source Noutou clock expires.

    The matching player VMD is a passthrough track so Resharped's modern full-body
    Piercing clip does not fight the classic blade path. Movement/hit timing stays
    entirely in modern Java.
    """
    recovery=PIERCING_ACTIVE_FRAME+legacy_reset_frames(combos['Stinger'])
    blade=[]
    for f in range(PIERCING_MAX_FRAME+1):
        for bone,sheath in [('hardpointA',False),('hardpointB',True)]:
            idle=pose(combos['None'],0,sheath)
            if f<PIERCING_ACTIVE_FRAME:
                result=idle
            elif f<recovery:
                result=pose(combos['Stinger'],1,sheath)
            else:
                result=noutou_recovery_pose(f,recovery,combos,sheath)
            blade.append(Key(bone,f,*result))
    for bone in ('センター','JointA1','JointA2','JointA3','JointB1','JointB2','JointB3'):
        for f in (0,PIERCING_MAX_FRAME):
            blade.append(Key(bone,f))
    player=[Key('classic_root',f) for f in range(PIERCING_MAX_FRAME+1)]
    # VMD model-name field is 20 bytes (CP932). Keep these deliberately short.
    return (Motion('Classic Stinger',blade),
            Motion('Classic Piercing',player),recovery)

def generate(output):
    legacy=json.loads((ROOT/'data/legacy_motion_map.json').read_text())
    combos={x['name']:x for x in legacy['entries']}
    slots=json.loads((ROOT/'data/bake_slots.json').read_text())['slots']
    modern=json.loads((ROOT/'data/resharped_blade_frame_map.json').read_text())['entries']
    keys={};report=[]
    for slot in slots:
        adaptation=slot.get('adaptation')
        if adaptation not in ADAPTATION_CLASSES:
            raise ValueError(f"{slot['name']} has invalid adaptation class {adaptation!r}")
        start,end=slot['start'],slot['end'];recovery=resolve_recovery(slot,combos)
        name=slot['legacy'];combo=combos[name]
        source_timeout=slot.get('recovery_mode')=='legacy_reset'
        target=timeout_target(slot,combos) if source_timeout else None
        # The six-tick ordinary legacy swing is nine VMD frames at 30 Hz.
        # Long modern windows keep a hold; they do not stretch the slash.
        for f in range(start,end+1):
            elapsed=f-start
            for bone,sheath in [('hardpointA',False),('hardpointB',True)]:
                if f<recovery:
                    segments=[s for s in slot.get('segments',[]) if f>=s['start']]
                    if segments:
                        segment=segments[-1];active=combos[segment['legacy']]
                        t=(f-segment['start'])/segment.get('frames',VANILLA_SWING_FRAMES)
                    elif 'second_legacy' in slot and f>=slot['second_start']:
                        active=combos[slot['second_legacy']];t=(f-slot['second_start'])/VANILLA_SWING_FRAMES
                    else:active=combo;t=max(0,elapsed-slot.get('attack_offset',0))/slot.get('swing_frames',VANILLA_SWING_FRAMES)
                    result=pose(active,min(1,t),sheath)
                else:
                    idle=pose(combos['None'],0,sheath)
                    if source_timeout:
                        # Reproduce the old state transition instead of inventing
                        # a long modern recovery. Saya/Iai-family/Noutou moves
                        # reset to None. Other blade moves enter Noutou, run a
                        # fresh six-tick swing, then hold its final pose until the
                        # delayed source Noutou state actually expires.
                        if target=='none':
                            result=idle
                        else:
                            result=noutou_recovery_pose(f,recovery,combos,sheath)
                    else:
                        last_name=slot['segments'][-1]['legacy'] if slot.get('segments') else slot.get('second_legacy',name)
                        active=combos[last_name]
                        last=pose(active,1,sheath)
                        span=end-recovery
                        if combo['scabbard']:
                            # Legacy candidate behavior retained for slots whose
                            # timeout has not yet been source-verified.
                            t=(f-recovery)/max(1,span)
                            result=mix(last,idle,t)
                        else:
                            # Legacy candidate behavior retained for unverified
                            # slots: short bridge -> Noutou -> neutral.
                            nstart=pose(combos['Noutou'],0,sheath)
                            elapsed=f-recovery
                            bridge=min(3,span/4);swing=min(VANILLA_SWING_FRAMES,span-bridge)
                            if span==0:result=idle
                            elif elapsed<bridge:result=mix(last,nstart,elapsed/bridge)
                            elif elapsed<bridge+swing:result=pose(combos['Noutou'],(elapsed-bridge)/swing,sheath)
                            else:result=idle
                keys[(bone,f)]=Key(bone,f,*result)
        neutral=(recovery+noutou_state_frames(combos)) if target=='noutou' else recovery
        report.append(dict(slot=slot['name'],legacy=name,adaptation=adaptation,frames=[start,end],recovery=recovery,
                           timeout_target=target,neutral=min(end,neutral),status=slot['status']))
    # Fill genuinely unused gaps with neutral pose. Never interpolate across slots.
    max_frame=max(r['end'] for r in modern if r['resource']=='slashblade:combostate/motion.vmd')
    for f in range(max_frame+1):
        for bone,sheath in [('hardpointA',False),('hardpointB',True)]:
            keys.setdefault((bone,f),Key(bone,f,*pose(combos['None'],0,sheath)))
    # Reset all upstream chain bones; hardpoints contain the complete transform.
    for bone in ('センター','JointA1','JointA2','JointA3','JointB1','JointB2','JointB3'):
        for f in (0,max_frame):keys[(bone,f)]=Key(bone,f)
    dest=output/'assets/slashblade';(dest/'combostate').mkdir(parents=True,exist_ok=True)
    (dest/'model/pa').mkdir(parents=True,exist_ok=True)
    (dest/'combostate/motion.vmd').write_bytes(Motion('Classic r32 bake',list(keys.values())).encode())
    # The source has no skeletal clips. Preserve the game-supplied player pose
    # through an explicit rig adapter; do not advertise these neutral keys as a
    # recovered r32 body-animation asset.
    player=Motion('Classic passthrough',[Key('classic_root',f) for f in range(max_frame+1)])
    (dest/'model/pa/player_motion.vmd').write_bytes(player.encode())
    (dest/'model/pa/alex.pmd').write_bytes(passthrough_pmd())

    piercing,piercing_player,piercing_recovery=classic_piercing_motions(combos)
    (dest/'combostate/piercing.vmd').write_bytes(piercing.encode())
    (dest/'combostate/piercing_pl.vmd').write_bytes(piercing_player.encode())
    report.append(dict(slot='Piercing dedicated atlas',legacy='Stinger',adaptation='CLASSIC_INTERPRETATION',
                       frames=[1,PIERCING_MAX_FRAME],recovery=piercing_recovery,
                       timeout_target='noutou',neutral=min(PIERCING_MAX_FRAME,piercing_recovery+noutou_state_frames(combos)),
                       status='APPROXIMATE'))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'pack')
    a=ap.parse_args();print(json.dumps(generate(a.output),indent=2))
