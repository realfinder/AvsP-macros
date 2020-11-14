# -*- coding: utf-8 -*-

"""
Insert a line of Trims mod, based on the video frame bookmarks, at the 
current cursor position of the Avisynth script in the current tab.


Date: 2013-07-22 mod by AmjadSONY
Latest version:     https://github.com/vdcrim/avsp-macros
Doom9 Forum thread: http://forum.doom9.org/showthread.php?t=163653

Changelog:
- check if there's bookmarks
- let the user cancel if there's an odd number of bookmarks
- fix Python 2.6 compatibility


Copyright (C) 2011  Diego Fernández Gosende <dfgosende@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along 
with this program.  If not, see <http://www.gnu.org/licenses/gpl-2.0.html>.

"""

# run in thread
bm_list = avsp.GetBookmarkList()
if not bm_list:
    avsp.MsgBox(_('There is not bookmarks'), _('Error'))
    return
bm_list.sort()
trims = ''
for i, bm in enumerate(bm_list):
    if i<1:
        trims += 'Trim(0, {1})++'.format(bm_list[i - 1], bm-1)
    else:
        trims += 'Trim({0}, {1})++'.format(bm_list[i - 1], bm-1)
avsp.InsertText(trims[:-2] + '++Trim({0}, {1})'.format(bm, str(avsp.GetVideoFramecount() - 1)), pos=None)
