"""Lekmod code inside compiled-out preprocessor branches.

usage: python tools/dev/deadcode.py [pattern ...]   (default patterns: Lekmod, LEKMOD_, LTI_)
Prints every source line that matches a pattern but sits in a DEAD #if/#ifdef/#else branch, with the branch that kills it.
Defines are read from _Defines.h without its /* */ and // comments (AUI_CONSTIFY and AUI_WARNING_FIXES are only
mentioned inside comments there, so they are OFF; 2026-10-15). Conditions it can't evaluate (#if X && Y, numbers) count as live.
"""
import sys, re, glob, os
SRC = "C:/Users/bbruno/civ-tools/lek/LEKMOD_DLL/CvGameCoreDLL_Expansion2/"
_t = re.sub(r'/\*.*?\*/', '', open(SRC + '_Defines.h', encoding='latin-1').read(), flags=re.S)
_t = re.sub(r'//.*', '', _t)
DEFS = set(re.findall(r'^\s*#define\s+(\w+)', _t, re.M)) | {"FINAL_RELEASE", "WIN32", "NDEBUG", "_WINDOWS", "CVGAMECOREDLL_EXPORTS"}
pats = sys.argv[1:] or ["Lekmod", "LEKMOD_", "LTI_"]

def evaluate(cond):
    """True/False for simple conditions, None when unknown"""
    c = cond.strip()
    m = re.match(r'#\s*ifdef\s+(\w+)', c)
    if m: return m.group(1) in DEFS
    m = re.match(r'#\s*ifndef\s+(\w+)', c)
    if m: return m.group(1) not in DEFS
    m = re.match(r'#\s*(?:el)?if\s+(.*)', c)
    if not m: return None
    e = re.sub(r'//.*', '', m.group(1)).strip()
    if not re.fullmatch(r'[\s()!&|\w]*', e): return None
    e2 = re.sub(r'defined\s*\(\s*(\w+)\s*\)', lambda mm: str(mm.group(1) in DEFS), e)
    e2 = re.sub(r'defined\s+(\w+)', lambda mm: str(mm.group(1) in DEFS), e2)
    if re.search(r'\b(?!True\b|False\b)[A-Za-z_]\w*', e2): return None
    e2 = e2.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
    try: return bool(eval(e2))
    except Exception: return None

for path in sorted(glob.glob(SRC + "*.cpp") + glob.glob(SRC + "*.h")):
    if os.path.basename(path) == "_Defines.h": continue
    stack = []   # [cond, live_of_this_branch, any_previous_branch_taken]
    incomment = False
    for n, line in enumerate(open(path, encoding='latin-1'), 1):
        s = line.strip()
        if s.startswith('#') and any(p in s for p in pats) and not all(b[1] for b in stack):
            dead = [b[0] for b in stack if not b[1]]
            print(f"{os.path.basename(path)}:{n}: {s[:90]}  <- DEAD under {dead[0][:60]}")
        if s.startswith('#'):
            if re.match(r'#\s*if', s):
                v = evaluate(s); live = True if v is None else v
                stack.append([s, live, live])
            elif re.match(r'#\s*elif', s) and stack:
                v = evaluate(s); live = (not stack[-1][2]) and (True if v is None else v)
                stack[-1][0] = s; stack[-1][1] = live; stack[-1][2] = stack[-1][2] or live
            elif re.match(r'#\s*else', s) and stack:
                stack[-1][1] = not stack[-1][2]; stack[-1][0] = '#else of ' + stack[-1][0]; stack[-1][2] = True
            elif re.match(r'#\s*endif', s) and stack:
                stack.pop()
            continue
        if any(p in line for p in pats) and not all(b[1] for b in stack):
            dead = [b[0] for b in stack if not b[1]]
            print(f"{os.path.basename(path)}:{n}: {s[:90]}  <- DEAD under {dead[0][:60]}")
