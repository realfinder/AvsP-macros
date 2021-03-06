# -*- coding: utf-8 -*-

"""
Split an AviSynth script into multiple trimmed avs

There's various dividing choices:
- Use the current AvsP bookmarks to delimit the Trims.  The first and 
  last frame are automatically added to the bookmarks if not already 
  present.
- Specify a frame step
- Specify a time step
- Specify a number of intervals

If 'split at the current cursor position' is set, the script is only 
evaluated until the line the cursor is on, and the Trims are inserted 
before the next one.  If this option and 'using the last evaluated 
expression' are checked, the clip that is used as the script's return 
is the one returned on the last evaluated expression, even if it's 
assigned to a variable (doesn't set 'last').


Date: 2012-11-13
Latest version:  https://github.com/vdcrim/avsp-macros

Changelog:
- fix Python 2.6 compatibility
- move all settings to the prompt
- add splitting options (bookmarks are not longer necessary)
- add 'split at current position' option
- fix file encodings and some cosmetics
- add 'using the last evaluated expression' option
- fix text evaluated when the cursor is on a multiline comment
- fix generated scripts not being correct in some cases
- strip tags and sliders from the script


Copyright (C) 2012  Diego Fernández Gosende <dfgosende@gmail.com>

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


# ------------------------------------------------------------------------------


# run in thread

import sys
import os
import os.path
import re

import pyavs

def parse_time(time):
    ''''Parse time (string) to ms
    
    >>> parse_time('01:23:45.678')
    5025678
    >>> parse_time('01:23:45')
    '''
    splits = re.split(r'[:.]', time)
    time_list = []
    try:
        for split in splits:
            time_list.append(int(split))
    except ValueError:
        return
    if len(time_list) != 4: return
    h, m, s, ms = time_list
    ms = ms + 1000 * (s + 60 * (m + 60 * h))
    return ms

def float_range_list(start, stop, step):
    '''float range (list) with stop included'''
    ret = []
    while start < stop:
        ret.append(int(round(start)))
        start += step
    ret.append(stop)
    return ret

self = avsp.GetWindow()

# Load default options
election = avsp.Options.get('election', _('using the current boomarks'))
frame_step = avsp.Options.get('frame_step', 10000)
time_step = avsp.Options.get('time_step', '0:01:00.000')
intervals = avsp.Options.get('intervals', 10)
use_current_position = avsp.Options.get('use_current_position', False)
use_last_expression = avsp.Options.get('use_last_expression', True)
use_dir = avsp.Options.get('use_dir', False)
use_base = avsp.Options.get('use_base', False)

# Get the default filename
filename = avsp.GetScriptFilename()
if filename:
    dirname, basename = os.path.split(filename)
elif self.version > '2.3.1':
    dirname, basename = os.path.split(avsp.GetScriptFilename(propose='general'))
else:
    dirname, basename = (self.options['recentdir'], self.scriptNotebook.GetPageText(
                         self.scriptNotebook.GetSelection()).lstrip('* '))
if use_dir:
    dirname = avsp.Options.get('dirname', '')
if use_base:
    basename = avsp.Options.get('basename', '')
basename2, ext = os.path.splitext(basename)
if ext in ('.avs', '.avsi'):
    basename = basename2
filename = os.path.join(dirname, basename)

# Ask for options
while True:
    election_list = (_('using the current boomarks'), _('specifying a frame step'), 
                     _('specifying a time step'), _('specifying a number of intervals'), 
                     election)
    options = avsp.GetTextEntry(title=_('Divide script'), 
        message=[_('Split script by...'), 
                 [_('Frame step'), _('Time step'), _('Number of intervals')], 
                 [_('Split at the current cursor position'), 
                  _('... using the last evaluated expression')],
                 _('Choose a directory and basename'),
                 [_('Use always this directory'), _('Use always this basename')]], 
        default=[election_list, 
                 [(frame_step, 1, None, 0, max(1, 10 ** (len(str(frame_step)) - 2))), 
                  time_step, (intervals, 1)], 
                 [use_current_position, use_last_expression], 
                 filename, [use_dir, use_base]], 
        types=['list_read_only', ['spin', '', 'spin'], ['check', 'check'], 
               'file_save', ['check', 'check']], 
        width=400)
    if not options:
        return
    (election, frame_step, time_step, intervals, use_current_position, 
     use_last_expression, filename, use_dir, use_base) = options          
    if election == _('specifying a time step'):
        time_step_ms = parse_time(time_step)
        if not time_step_ms:
            avsp.MsgBox(_('Malformed time: '+ time_step), _('Error'))
            continue
    if filename:
        filename = filename.lstrip()
        break
    elif not avsp.MsgBox(_('An output path is needed'), _('Error'), True):
        return

# Save default options
avsp.Options['election'] = election
avsp.Options['frame_step'] = frame_step
avsp.Options['time_step'] = time_step
avsp.Options['intervals'] = intervals
avsp.Options['use_current_position'] = use_current_position
avsp.Options['use_last_expression'] = use_last_expression
avsp.Options['use_dir'] = use_dir
avsp.Options['use_base'] = use_base
if use_dir:
    avsp.Options['dirname'] = os.path.dirname(filename)
if use_base:
    avsp.Options['basename'] = os.path.basename(filename)

# Eval script
encoding = sys.getfilesystemencoding()
if self.version > '2.3.1':
    text = avsp.GetText(clean=True) 
else:
    text = self.getCleanText(avsp.GetText())
var = 'last'
assign = ''
if use_current_position:
    text = text.encode('utf-8') # StyledTextCtrl uses utf-8 internally
    script = self.currentScript
    re_assign = re.compile(r'\s*(\w+)\s*=')
    for line in range(script.GetCurrentLine(), -1 , -1):
        line_text = script.GetLine(line).strip()
        line_pos = script.PositionFromLine(line)
        if (line_text and script.GetStyleAt(line_pos) not in script.commentStyle):
            if use_last_expression:
                match = re_assign.match(line_text)
                if match:
                    var = match.group(1)
                    assign = '{0}={0}.'.format(var)
            script.SetCurrentPos(line_pos)
            script.SetAnchor(line_pos)
            break
    index = script.GetLineEndPosition(script.GetCurrentLine())
    text_enc = text[:index], text[index:]
    text = text_enc[0].decode('utf-8')
    if encoding != 'utf8': # AviSynth expects mbcs
        text_enc = (text.encode(encoding).rstrip(), 
                    text_enc[1].decode('utf-8').encode(encoding))
else:
    text_enc = text.encode(encoding).rstrip(), ''
clip = pyavs.AvsClip(u'{0}\nreturn {1}'.format(text, var))
if not clip.initialized or clip.IsErrorClip():
    avsp.MsgBox(_('Error loading the script'), _('Error'))
    return
frame_count = clip.Framecount
fps = clip.Framerate
del clip

# Get the list of frames
if election == _('using the current boomarks'):
    frame_list = avsp.GetBookmarkList()
    if not frame_list:
        avsp.MsgBox(_('There is not bookmarks'), _('Error'))
        return
    frame_list.sort()
    if frame_list[0] != 0:
        frame_list[:0] = [0]
    if frame_list[-1] == frame_count - 1:
        frame_list[-1] = frame_count
    else:
        frame_list.append(frame_count)
elif election == _('specifying a frame step'):
    frame_list = float_range_list(0, frame_count, frame_step)
elif election == _('specifying a time step'):
    frame_list = float_range_list(0, frame_count, fps *  time_step_ms / 1000)
elif election == _('specifying a number of intervals'):
    frame_list = float_range_list(0, frame_count, frame_count / float(intervals))

# Save scripts
global avs_list
avs_list = []
filename2, ext = os.path.splitext(filename)
if ext in ('.avs', '.avsi'):
    filename = filename2
digits = len(str(len(frame_list) - 1))
for i, frame in enumerate(frame_list[:-1]):
    avs_path = u'{0}_{1:0{2}}.avs'.format(filename, i+1, digits)
    avs_list.append(avs_path)
    with open(avs_path, 'w') as f:
        f.write(text_enc[0] + 
                '\n{0}Trim({1},{2})'.format(assign, frame, frame_list[i+1] - 1).encode(encoding) + 
                text_enc[1])
return avs_list
