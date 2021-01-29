# GPo 2020, Next tab to current frame time.py
# Changes the tab and shows the video frame from the previous frame time code
# So there must be a second tab with a changed frame rate

import wx
self = avsp.GetWindow()

script = self.currentScript
if script.AVI is None:
    wx.Bell()
    return
    
frame = self.GetFrameNumber()
try:
    tc = frame/self.MacroGetVideoFramerate()
except:
    wx.Bell()
    return

self.SelectTab(index=None, inc=1)
script = self.currentScript

try:
  frame = int(round(tc * self.MacroGetVideoFramerate()))
except:
    wx.Bell()
    return

if frame < 0 or (script.AVI and frame >= script.AVI.Framecount):
    wx.Bell()
    return
    
self.ShowVideoFrame(frame)