import wx
re=avsp.GetTextEntry(_('Start from first scene:'), True, 
                     _('Select scene start'), 'check', 200)
if re == '':
    return

filename = avsp.GetFilename(_('Select the scene file'), filefilter=
                            _('Log files') + '|*.log|' +
                            _('Log and Text files') + '|*.txt;*.log|' +
                            _('All files') + ' (*.*)|*.*')

if not filename:
    return
self = avsp.GetWindow()  
txt = self.GetTextFromFile(filename)[0]
txt = txt.strip()
first = re
bookmarkDict = {}
lines = txt.split('\n')
count = len(lines)

try:
    for index, line in enumerate(lines):
        s = line.strip()
        if not s.isdigit():
            raise 
        if first:
            if index == 0:
                bookmarkDict[int(s)] = 1
                if index < count -1:
                    s = lines[index+1].strip()
                    if not s.isdigit(): break
                    bookmarkDict[int(s)-1] = 2
            elif index % 2 == 0:
                bookmarkDict[int(s)] = 1
                if index < count -1:
                    s = lines[index+1].strip()
                    if not s.isdigit(): break
                    bookmarkDict[int(s)-1] = 2
        elif index > 0 and index % 2 != 0:
            bookmarkDict[int(s)] = 1
            if index < count -1:
                s = lines[index+1].strip()
                if not s.isdigit(): break
                bookmarkDict[int(s)-1] = 2 
except:
    bookmarkDict = {}
    avsp.MsgBox(_('Error reading scenes'), _('Error'))
    
if bookmarkDict:
    items = bookmarkDict.items()
    for i, item in enumerate(items):
        value, bmtype = item
        self.AddFrameBookmark(value, bmtype, refreshVideo=False)