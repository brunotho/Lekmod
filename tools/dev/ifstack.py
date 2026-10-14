import sys,re
SRC="C:/Users/bbruno/civ-tools/lek/LEKMOD_DLL/CvGameCoreDLL_Expansion2/"
defs=set(re.findall(r'^\s*#define\s+(\w+)', open(SRC+'_Defines.h',encoding='latin-1').read(), re.M))
for f,pat in [a.split(':',1) for a in sys.argv[1:]]:
    stack=[]
    for n,l in enumerate(open(SRC+f,encoding='latin-1'),1):
        s=l.strip()
        if s.startswith('#if'): stack.append([s,False])
        elif s.startswith('#else') or s.startswith('#elif'):
            if stack: stack[-1][1]=True
        elif s.startswith('#endif'):
            if stack: stack.pop()
        if pat in l:
            conds=[]
            for c,inelse in stack:
                m=re.match(r'#if(n?def)?\s*(!?)\s*(?:defined\()?\s*(\w+)\)?',c)
                if not m: conds.append(c); continue
                neg = (m.group(1)=='ndef') or (m.group(2)=='!')
                name=m.group(3); live=(name in defs)!=neg
                if inelse: live=not live
                conds.append(f"{c}{' [else]' if inelse else ''} -> {'LIVE' if live else 'DEAD'}")
            print(f"{f}:{n} {pat[:40]!r}: {conds}")
