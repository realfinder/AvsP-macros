# -*- coding: utf-8 -*-

"""
Create a x264 QP file from a Matroska chapter file

This macro takes a Matroska chapter file, gets the starting time 
of every chapter and writes a QP file marking those frames as key 
frames.

The frame rate of the video is needed.  A constant fps value can be 
obtained from the script in the current tab or introduced directly. 
Timecodes format v1 and v2 files are also accepted.

Current issues:
- Unnecessary key frames may be added with some ordered chapters


Date: 2017-07-02 mod
Latest version:  https://github.com/vdcrim/avsp-macros


Copyright (C) 2013  Diego Fernández Gosende <dfgosende@gmail.com>

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

# PREFERENCES

# Suffix list for automatic search of a chapter and timecode file
chapters_suffix = ['_Chapters.xml', '_Chapters.ogm', '.chapters.xml', '.xml', '.ogm', '.txt']
tc_suffix = ['.otc.txt', '.tc.txt', '.timecode.txt', '.timecodes.txt', '.txt']


# ------------------------------------------------------------------------------


# run in thread
import os.path
import re

def time2ms(time):
    return ((int(time[0]) * 60 + int(time[1])) * 60 + float(time[2]+"."+time[3])) * 1000

def timecode_v1_to_v2(lines, offset=0, start=0, end_frame=None, end_ms=None, 
                      default=24/1.001, float_list=False):
    """Convert a timecode v1 file to v2
    
    lines: list of lines of the timecode v1 file (excluding header)
    offset:    starting time (ms)
    start:     first frame
    end_frame: last frame
    end_ms:    last timecode
    default:   FPS used if 'assume' line isn't present
    
    Returns the list of timecode v2 lines (str)
    
    """
    # Generate all intervals
    inters = []
    all_inters =[]
    try:
        default = float(lines[0].split()[1])
        i = 1
    except IndexError:
        i = 0
    inters = [[int(line[0]), int(line[1]), float(line[2])] for line in 
                                [line.strip().split(',') for line in lines[i:]]]
    if start < inters[0][0]:
        all_inters.append([start, inters[0][0] - 1, default])
    try:
        for i, inter in enumerate(inters):
            all_inters.append(inter)
            if inters[i+1][0] - inter[1] > 1:
                all_inters.append([inter[1] + 1, inters[i+1][0] - 1, default])
    except IndexError:
        if end_frame is not None and end_frame > inters[-1][1]:
            all_inters.append([inters[-1][1] + 1, end_frame, default])
    
    # v1 -> v2
    v2 = [] if offset else [0.0]
    for inter in all_inters:
        ms = 1000.0 / inter[2]
        for i in range(1, inter[1] - inter[0] + 2):
            v2.append(ms * i + offset)
        offset = v2[-1]
    if end_ms is not None:
        i = 1
        while v2[-1] < end_ms:
            v2.append(ms * i + offset)
            i += 1
    if float_list:
        return v2
    return ['{0:.3f}\n'.format(tc) for tc in v2]

# Ask for options
avs = avsp.GetScriptFilename()
chapters_path = tc_path = qpfile_path = ''
if avs:
    avs_no_ext = os.path.splitext(avs)[0]
    for path in (avs_no_ext + suffix for suffix in chapters_suffix):
        if os.path.isfile(path):
            chapters_path = path
            break
    for path in (avs_no_ext + suffix for suffix in tc_suffix):
        if os.path.isfile(path):
            tc_path = path
            break
    qpfile_path = avs_no_ext + '.qpf'
fps_str = avsp.Options.get('fps', '24')
fps_from_script = avsp.Options.get('fps_from_script', False)
xml_filter = (_('Supported files') + '|*.xml;*.ogm;*.txt|' + _('XML files') + ' (*.xml)|*.xml|' + _('OGM files') + ' (*.ogm)|*.ogm|' + _('Text files') + ' (*.txt)|*.txt|' + _('All files') + '|*.*')
tc_filter = (_('Text files') + ' (*.txt)|*.txt|' + _('All files') + '|*.*')
qpf_filter = (_('QP files') + ' (*.qp;*.qpf;*.qpfile)|*.qp;*.qpf;*.qpfile|' +
              _('All files') + '|*.*')
while True:
    options = avsp.GetTextEntry(
        title=_('QP file from Matroska chapter file'), 
        message=[
            _('chapter file'),
            [_('Frame rate'), _('Get the FPS from the script')], 
            _('Use a timecode file (v1 or v2) instead'),
            _('Output QP file (blank -> same name as chapter file)'),
            ],
        default=[
            (chapters_path, xml_filter),
            [('23.976', '24', '25', '29.970', '30', '50', '59.940', fps_str),
             fps_from_script],
            (tc_path, tc_filter),
            (qpfile_path, qpf_filter)
            ],
        types=[
            'file_open', ['list_writable', 'check'], 'file_open', 'file_save'])
    if not options:
        return
    chapters_path, fps_str, fps_from_script, tc_path, qpfile_path = options
    if not chapters_path:
        avsp.MsgBox(_('A chapter file is needed!'), _('Error')) 
        continue
    if tc_path:
        cfr = False
    else:
        if fps_from_script:
            fps = avsp.GetVideoFramerate()
            if not fps:
                return
        else:
            if fps_str == '23.976':
                fps = float(24/1.001)
            elif fps_str == '29.970':
                fps = float(30/1.001)
            elif fps_str == '59.940':
                fps = float(60/1.001)
            else:
                try:
                    fps = float(fps_str)
                except:
                    avsp.MsgBox(_('Incorrect frame rate'), _('Error'))
                    continue
        cfr = True
    break
avsp.Options['fps'] = fps_str
avsp.Options['fps_from_script'] = fps_from_script
if not qpfile_path:
    qpfile_path = os.path.splitext(chapters_path)[0] + '.qpf'

# Get chapter start times
if ".xml" in chapters_path:
    re_chapters = re.compile(ur'^.*<ChapterTimeStart>\s*(\d+):(\d+):(\d+)\.(\d+)'
                         ur'\s*</ChapterTimeStart>.*$')
else:
						 re_chapters = re.compile(ur'^.*=\s*(\d+):(\d+):(\d+)\.(\d+)'
                         ur'\s*.*$')
						 
chapters_ms = set()
with open(chapters_path) as file:
    for line in file:
        chapter = re_chapters.search(line)
        if chapter:
            chapters_ms.add(time2ms([int(g) for g in chapter.groups()]))
chapters_ms = sorted(chapters_ms)
if not chapters_ms[0]:
    del chapters_ms[0]
if not chapters_ms:
    avsp.MsgBox(_('No chapter starting times in file!'), _('Error'))
    return

# Convert ms to frame number
frames = []
if cfr:
    for ms in chapters_ms:
        frames.append(int(round(ms / 1000 * fps)))
else:
    # Read timecode file. Convert v1 -> v2
    with open(tc_path) as itc:
        header = itc.readline().strip()
        if header == '# timecode format v2':
            tcs = [float(line) for line in itc.readlines()]     
        elif header == '# timecode format v1':
            tcs = timecode_v1_to_v2(itc.readlines(), end_ms=chapters_ms[-1], 
                                    float_list=True)
        else:
            avsp.MsgBox(_('Invalid timecode file'), _('Error'))
            return
    
    j = 0
    for i, tc in enumerate(tcs):
        if tc >= chapters_ms[j]:
            if abs(tc - chapters_ms[j]) < abs(tcs[i - 1] - chapters_ms[j]):
                frames.append(i)
            else:
                frames.append(i - 1)
            if j + 1 == len(chapters_ms):
                break
            j += 1
        i += 1

# Save to file
with open(qpfile_path, 'w') as f:
    f.writelines(['{0} I\n'.format(frame) for frame in frames])