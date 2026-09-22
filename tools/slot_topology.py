"""Helpers for reasoning about Resharped's shared VMD atlas windows.

The resource pack cannot branch on ComboState at runtime.  If two semantic moves
consume the same VMD frames, those frames must therefore use a compromise motion.
These helpers make that constraint machine-checkable instead of relying on a
hand-maintained mental map.
"""

MOTION_RESOURCE = 'slashblade:combostate/motion.vmd'


def overlap_frames(a, b):
    """Inclusive frame intersection size."""
    lo = max(int(a['start']), int(b['start']))
    hi = min(int(a['end']), int(b['end']))
    return max(0, hi - lo + 1)


def relation(a, b):
    """Describe how two inclusive atlas ranges relate.

    A single shared boundary frame is TOUCH, not a meaningful shared animation
    window.  Resharped commonly ends one state on the same frame where the next
    state starts.
    """
    count = overlap_frames(a, b)
    if count == 0:
        return 'DISJOINT'
    if count == 1 and (
        int(a['end']) == int(b['start']) or int(b['end']) == int(a['start'])
    ):
        return 'TOUCH'
    if int(a['start']) == int(b['start']) and int(a['end']) == int(b['end']):
        return 'EXACT'
    if int(a['start']) <= int(b['start']) and int(a['end']) >= int(b['end']):
        return 'CONTAINS'
    if int(b['start']) <= int(a['start']) and int(b['end']) >= int(a['end']):
        return 'CONTAINED'
    return 'PARTIAL'


def motion_entries(frame_map):
    return [
        entry for entry in frame_map['entries']
        if entry.get('resource') == MOTION_RESOURCE
    ]


def by_id(frame_map):
    return {entry['id']: entry for entry in motion_entries(frame_map)}


def family_window(frame_map, ids):
    index = by_id(frame_map)
    selected = [index[combo_id] for combo_id in ids]
    return {
        'start': min(entry['start'] for entry in selected),
        'end': max(entry['end'] for entry in selected),
    }


def meaningful_consumers(frame_map, window, exclude_ids=()):
    """Return motion.vmd consumers sharing 2+ frames with *window*.

    One-frame boundary touches are intentionally excluded because they do not
    force two moves to share a visible clip.
    """
    excluded = set(exclude_ids)
    return [
        entry for entry in motion_entries(frame_map)
        if entry['id'] not in excluded and overlap_frames(entry, window) >= 2
    ]


def external_consumers(frame_map, ids):
    window = family_window(frame_map, ids)
    return meaningful_consumers(frame_map, window, exclude_ids=ids)
