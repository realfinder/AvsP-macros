# GPo 2020
import wx

bmlist = avsp.GetBookmarkList(title=False)
if not bmlist:
    wx.MessageBox(_('No bookmarks defined.'), _('Error'), style=wx.OK|wx.ICON_ERROR)
    return

bmlist.sort()
count = len(bmlist)
txt = 'c0=Trim(0, {})\n'.format(bmlist[0]-1)
c = 1
for i in xrange(count):
    if i < count-1:
        start = bmlist[i]
        end = bmlist[i+1]-1
    else:
        start = bmlist[i]
        end = 0
    txt += 'c{}=Trim({}, {})\n'.format(c, start, end)
    c += 1
    
avsp.InsertText(txt, pos=None)