import os
import os.path
import pyavs
import re
import sys

sel = ''
sep = '"'
global IsFuncOn
maxPrefetch = 64  # min 8

if maxPrefetch < 8:
    maxPrefetch = 8

self = avsp.GetWindow()

MyBookmarks = ''
txt = ''
txt_lines =[]
tmp_lines = []
tmp_lines =  avsp.GetText(index=None, clean=False).strip().encode(sys.getfilesystemencoding()).split('\n')
# remove MyBookmark lines and store it
for line in tmp_lines:
    if line.find('#Bookmarks:') > -1:
        MyBookmarks += line + '\n'
    else :
        txt += line + '\n'
        txt_lines.append(line)

if txt == '':
    return

# Get source file name if selected
sel = avsp.GetSelectedText()

if sel and not os.path.isdir(os.path.split(sel)[0]):
    sel = ''

# if not sel, find source file name
if not sel:
    i = txt.find('SourceFile : "')
    if i < 0:
        i = txt.find( 'ScriptDir()')
    if i < 0:
        i = txt.find('("')
    if i > -1:
        s = txt[i : len(txt)]
        a =[]
        a = s.split(sep)
        sel = a[1]

if sel:
    dir, file = os.path.split(sel)
    if file:
        sel = 'String(ScriptDir()) + ' + '"' + file + '"'
    else:
        sel = '"' + sel + '"'

def IsOn(s):
    if s != '':
        sp = s.split('\n')
        for line in sp:
            if not line.startswith('#'):
                return True
    return False

# Can find multiple Instances and func's with line breaks
def FindFunc3(fu, L=None, ignor=False, onlyOne=False):
    global IsFuncOn
    i = 0
    rs = ''
    while (i > -1) and (i < len(txt)-1):
        i = txt.lower().find(fu.lower(), i)
        if i > -1:
            if (i > 0) and ((txt[i-1] == '#') and ignor):  # skip if ignor
                i += 1
                continue
            # skip if found funcName not word start eg. (TUnsharp, unsharp)
            if (i > 0) and (txt[i-1] != '#') and (txt[i-1] != ' ') and (txt[i-1] != '\n'):
                i += 1
                continue
            #dec found index if func disabled '#'
            if (i > 0) and (txt[i-1] == '#'):
                e = i-1
            else:
                e = i
            s = txt[e : len(txt)]

            ### find funcEnd
            a = 0; b = 0; e = 0
            for x in range(0, len(s)):
                if s[x] == '(':
                    a += 1
                if s[x] == ')':
                    b += 1
                if (a > 0) and (b >= a):
                    e = x
                    break

            if e > 0:
                i = i  + e
               # inc s to line endPos
                while (e < len(s)) and (not s[e+1:e+2] in ['\n']):
                    e += 1
                s = s[: e+1].strip()
                if IsOn(s):
                    IsFuncOn = True
                rs += s  + '\n'
                if onlyOne and IsOn(s):
                    break
            else:
                rs += '### Error cannot find funcEnd:' + fu + '\n'
                i += 1

    if rs != '':
        rs = rs[:-1]
        if L != None:
            L.append(rs)
    return rs


# can find multiple instances but cannot find func's with line breaks
def FindFunc2(fu, L=None, ignor=False, onlyOne=False):
    rs = ''
    for line in txt_lines:
        i = line.lower().find(fu.lower())
        if i > -1:
            if (i > 0) and ((line[i-1] == '#') and ignor):
                continue
            else:
                rs += line.strip() + '\n'
                if onlyOne:
                    break

    if rs != '':
        rs = rs[:-1]
        if (L != None) and (rs != ''):
            L.append(rs)
    return rs

# can only find one Instance of the func and no line breaks
def FindFunc(fu, L=None, ignor=False):
    i = txt.lower().find(fu.lower())
    if i > -1:
        if (i > 0) and ((txt[i-1] == '#') and ignor):
            return ''
        if (txt[i-1] == '#'):
            i = i-1
        s = txt[i : len(txt)]
        i = s.find(')')
        if i > -1:
            while (i < len(s)) and not (s[i+1:i+2] in ['\n']):
                i += 1
            if L != None:
                L.append(s[0 : i+1].strip())
            return s[0 : i+1].strip()
    return ''

txt2 = ['']
txt2.append(r'MP_Pipeline("""')
txt2.append(r'### inherit start ###')

txt2.append(r'SourceFile = ' + sel)
txt2.append(r'SourceFile = Exist(SourceFile) ? SourceFile : "' + dir + '\\' + file + '"')
txt2.append(r'### inherit end ###')
txt2.append('')
s = FindFunc(r'LSMASHVideoSource', None, True)
if s:
   txt2.append(r'LSMASHVideoSource(SourceFile)')
else:
   txt2.append(r'LWLibavVideoSource(SourceFile, cache=False)')

FindFunc('SelectEven(', txt2)

txt2.append(r'# ### prefetch: ' + str(maxPrefetch) + ', ' + str(int(maxPrefetch/2)))
txt2.append(r'### ###')
FindFunc('QTGMC(', txt2, True)
FindFunc('KTGMC(', txt2, True)
txt2.append(r'### platform: Win32')
txt2.append('v=HDRAGC(coef_gain=1.0, max_gain=3.0,min_gain=1.0,coef_sat=1.0,max_sat=9.0,min_sat=0.0,avg_lum=128,avg_window=24,corrector=1.0,\n' +
            '\\reducer=0.0,response=100,protect=2,mode=2,passes=4,black_clip=0.0,shift=0,shift_u=0,shift_v=0,freezer=-1,shadows=true,debug=0)\nhdr2(v, 0.5)')
txt2.append(r'### platform: Win64')
txt2.append(r'### ###')
s = FindFunc('audio=LSMASHAudioSource', None, True)
if s:
    txt2.append(r'audio=LSMASHAudioSource(SourceFile)')
    txt2.append(r'audioDub(last, audio)')
else:
    s = FindFunc('audio=LWLibavAudioSource')
    if s:
        txt2.append(r'audio=LWLibavAudioSource(SourceFile, cache=False)')
        txt2.append(r'audioDub(last, audio)')
txt2.append('return last')
txt2.append('""")')
txt2.append('')

s = '\n'.join(map(str, txt2))
avsp.InsertText('*/\n' + s, pos=None)
avsp.InsertText('/*', pos=0)



