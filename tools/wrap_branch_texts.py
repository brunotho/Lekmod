"""Pre-wrap the [ICON_BULLET] lines of the policy branch help texts (their tooltip on the branch picture comes straight from XML,
so the Lua hanging indent can't reach it). Same width estimate as LekmodHangingIndent in SocialPolicyPopup.lua."""
import re
import os
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'LEKMOD', 'Override', 'CIV5Units_Mongol.xml')
LIMIT = 250          # the branch picture tooltip wraps at about 275 px
INDENT = '     '
NARROW = {' ': 4, 'i': 3, 'l': 3, 'j': 3, '.': 3, ',': 3, ';': 3, ':': 3, "'": 3, '!': 3, '|': 3,
          'f': 4, 't': 4, 'r': 4, '(': 4, ')': 4, 'I': 4, 'm': 10, 'w': 9, 'M': 11, 'W': 11, '%': 9}

def width(s):
    s = re.sub(r'\[COLOR_\w+\]|\[ENDCOLOR\]', '', s)
    w = 22 * len(re.findall(r'\[ICON_\w+\]', s))
    s = re.sub(r'\[ICON_\w+\]', '', s)
    for c in s:
        w += NARROW.get(c, 8 if c.isupper() else 6.5)
    return w * 1.18

def wrap(text):
    out = []
    for line in text.split('[NEWLINE]'):
        if line.startswith('[ICON_BULLET]') and width(line) > LIMIT:
            cur = ''
            for word in line.split():
                cand = word if cur == '' else cur + ' ' + word
                if cur != '' and width(cand) > LIMIT:
                    out.append(cur)
                    cur = INDENT + word
                else:
                    cur = cand
            out.append(cur)
        else:
            out.append(line)
    return '[NEWLINE]'.join(out)

t = open(T, 'rb').read().decode('utf-8')
for b in ['TRADITION', 'LIBERTY', 'HONOR', 'PIETY', 'PATRONAGE', 'AESTHETICS', 'COMMERCE', 'RATIONALISM', 'EXPLORATION']:
    tag = 'TXT_KEY_POLICY_BRANCH_%s_HELP' % b
    assert t.count('Tag="%s"' % tag) == 1, tag
    i = t.index('Tag="%s"' % tag)
    a = t.index('<Text>', i) + len('<Text>')
    e = t.index('</Text>', a)
    body = ' '.join(t[a:e].split())
    # undo an earlier pre-wrap so the script can be rerun
    body = re.sub(r'\[NEWLINE\] +', ' ', body)
    new = wrap(body)
    t = t[:a] + '\n\t\t\t\t' + new + '\n\t\t\t' + t[e:]
    print(b)
    for l in new.split('[NEWLINE]'):
        print('  ', re.sub(r'\[COLOR_\w+\]|\[ENDCOLOR\]', '', l))
open(T, 'wb').write(t.encode('utf-8'))
