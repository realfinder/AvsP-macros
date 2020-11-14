# -*- coding: utf-8 -*-

"""
Crop borders from the script in the current tab


Date: 2012-10-24
Latest version: https://github.com/vdcrim/avsp-macros

Changelog:
- fix Python 2.6 compatibility
- fix number of samples
- speed up a bit the autocrop detection if the original AviSynth clip is
  keep on memory (%YUV or %CLR are set to appear on the status bar)
- check the chroma subsampling also for the new AviSynth 2.6 colorspaces
  (AvsPmod 2.4.0+)
- fix clips with less frames than samples


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

# PREFERENCES  

# Set to False to not ask for settings
show_prompt = True

# Values used with show_prompt = False
samples = 10  # number of frames analyzed. Start and end of the video are skipped to avoid credits
tol = 70  # tolerance (0-255)
overcrop = True # Up or down crop values because of chroma subsampling
insert = True  #  insert Crop() at the end of the script
refresh = True  # update and show if hidden the video preview


# ------------------------------------------------------------------------------


# run in thread
from collections import defaultdict
import wx

def autocrop(samples=10, tol=70, overcrop=True, insert=True, refresh=True, 
             show_prompt=False):
    """Crop borders from the script in the current tab"""
    # Get options
    if show_prompt:
        samples = avsp.Options.get('samples', samples)
        tol = avsp.Options.get('tol', tol)
        overcrop = avsp.Options.get('overcrop', overcrop)
        insert = avsp.Options.get('insert', insert)
        refresh = avsp.Options.get('refresh', refresh)
        options = avsp.GetTextEntry(
                message=[[_('Samples'), _('Tolerance'), _('Overcrop')], 
                         [_('Apply to script'), _('Update preview')]], 
                default=[[(samples, 1, 100), (tol, 0, 255), overcrop], 
                         [insert, refresh]], 
                title=_('Auto-crop'), 
                types=[['spin', 'spin', 'check'], ['check', 'check']], 
                width=200)
        if not options:
            return
        samples, tol, overcrop, insert, refresh = options
        avsp.Options['samples'] = samples
        avsp.Options['tol'] = tol
        avsp.Options['overcrop'] = overcrop
        avsp.Options['insert'] = insert
        avsp.Options['refresh'] = refresh

    # Get crop values for a number of frames
    frames = avsp.GetVideoFramecount()
    avs = avsp.GetWindow().currentScript
    if not frames or avs.AVI.IsErrorClip():
        avsp.MsgBox(_('Error loading the script'), _('Error'))
        return
    samples = min(samples, frames)
    if samples <= 2:
        frames = range(samples)
    else:
        def float_range(start=0, end=10, step=1):
            '''Range with float step'''
            while start < end:
                yield int(round(start))
                start += step
        frames = float_range(frames/10, 9*frames/10 - 1, 8.0*frames/(10*samples))
    progress = avsp.ProgressBox(samples, _('Analyzing frames...'), _('Auto-crop'))
    crop_values = []
    for i, frame in enumerate(frames):
        if not progress.Update(i)[0]:
            progress.Destroy()
            return
        crop_values.append(autocrop_frame(frame, tol))
    progress.Destroy()

    # Get final crop values
    final_crop_values = []
    for seq in zip(*crop_values):
        value = get_crop_value(seq)
        value = check_subsampling(value, avs.AVI.Colorspace, not len(final_crop_values) % 2, overcrop)
        final_crop_values.append(value)
    if insert:
        txt = '' if avsp.GetText().endswith('\n') else '\n'
        avsp.InsertText(txt + 'Crop({0}, {1}, -{2}, -{3})'.format(*final_crop_values))
        if refresh:
            avsp.ShowVideoFrame(forceRefresh=True)
    return final_crop_values

def autocrop_frame(frame, tol=70):
    """Return crop values for a specific frame"""
    avs_clip = avsp.GetWindow().currentScript.AVI
    width, height = avs_clip.vi.width, avs_clip.vi.height
    version = avsp.GetWindow().version
    if version > '2.3.1' or avs_clip.clipRaw is not None: # Get pixel color from the original clip
        avs_clip._GetFrame(frame)
        get_pixel_color = avs_clip.GetPixelRGB if avs_clip.IsRGB else avs_clip.GetPixelYUV
    else: # Get pixel color from the video preview (slower)
        bmp = wx.EmptyBitmap(width, height)
        mdc = wx.MemoryDC()
        mdc.SelectObject(bmp)
        avs_clip.DrawFrame(frame, mdc.GetHDC())
        img = bmp.ConvertToImage()
        get_pixel_color = lambda x, y : (img.GetRed(x, y), img.GetGreen(x, y), img.GetBlue(x, y))
    w, h = width - 1, height - 1
    top_left0, top_left1, top_left2 = get_pixel_color(0, 0)
    bottom_right0, bottom_right1, bottom_right2 = get_pixel_color(w, h)
    top = bottom = left = right = 0
    
    # top & bottom
    top_done = bottom_done = False
    for i in range(height):
        for j in range(width):
            if not top_done:
                color0, color1, color2 = get_pixel_color(j, i)
                if (abs(color0 - top_left0) > tol or 
                    abs(color1 - top_left1) > tol or 
                    abs(color2 - top_left2) > tol):
                        top = i
                        top_done = True
            if not bottom_done:
                color0, color1, color2 = get_pixel_color(j, h - i)
                if (abs(color0 - bottom_right0) > tol or 
                    abs(color1 - bottom_right1) > tol or 
                    abs(color2 - bottom_right2) > tol):
                        bottom = i
                        bottom_done = True
            if top_done and bottom_done: break
        else: continue
        break
    
    # left & right
    left_done = right_done = False
    for j in range(width):
        for i in range(height):
            if not left_done:
                color0, color1, color2 = get_pixel_color(j, i)
                if (abs(color0 - top_left0) > tol or 
                    abs(color1 - top_left1) > tol or 
                    abs(color2 - top_left2) > tol):
                        left = j
                        left_done = True
            if not right_done:
                color0, color1, color2 = get_pixel_color(w - j, i)
                if (abs(color0 - bottom_right0) > tol or 
                    abs(color1 - bottom_right1) > tol or 
                    abs(color2 - bottom_right2) > tol):
                        right = j
                        right_done = True
            if left_done and right_done: break
        else: continue
        break
    
    return left, top, right, bottom

def get_crop_value(seq):
    """Get the most repeated value on a sequence if it repeats more than 50%, 
    the minimum value otherwise"""
    d = defaultdict(int)
    for i in seq:
        d[i] += 1
    max = sorted(d.keys(), key=lambda x:-d[x])[0]
    if d[max] > len(seq) / 2:
        return max
    else:
        ret_val = max
        for value in seq:
            if value < ret_val:
                ret_val = value
        return ret_val

def check_subsampling(value, colorspace, horizontal, overcrop):
            '''Up or down crop values because of chroma subsampling'''
            colorspace = colorspace.lower()
            if colorspace in ('yuy2', 'yv16'):
                if value % 2 and horizontal:
                    if overcrop:
                        value += 1
                    else:
                        value -= 1
            elif colorspace == 'yv411':
                q, r = divmod(value, 4)
                if r and horizontal:
                    value = q * 4 + 4 if overcrop else q * 4
            elif colorspace == 'yv12' and value % 2:
                if overcrop:
                    value += 1
                else:
                    value -= 1
            return value

return autocrop(samples, tol, overcrop, insert, refresh, show_prompt)
