# GPo 2018, AvsPmod macro save image

"""
# find source file name for the image name and not the avs or script filename
# search for my pattern and find the source filename (sourceFile, videosource... etc)
# finds also ScriptDir() + "My Video.mkv"
# doesn't override any file
#
# My default AvsPmod templates eg 'mkv, ts, etc..':
#
# SourceFile = ScriptDir() + [***]
# SourceFile = Exist(SourceFile) ? SourceFile : ***
# video=LWLibavVideoSource(SourceFile, cache=False)
# audio=LWLibavAudioSource(SourceFile, cache=False)
# audioDub(video, audio)
"""

import os
import sys

# enable Input for filename if source file not found
# else filename is tab name (script name)
doMessage=True

sourceFile=''
fileName=''
# save as jpg
fnExt='.jpg'
# jpg Quality
jpgQ=90
framenr=''

# enable this for frame number, does not override existing files
#framenr= '_' + str(avsp.GetFrameNumber()) 

# for test
#fileName= avsp.GetScriptFilename()

if not fileName:
     sep = '"'
     txt = avsp.GetText(index=None, clean=False)
     i = txt.lower().find('sourcefile : "')
     if i < 0:
        i = txt.lower().find('videosource("')
     if i < 0:
        i = txt.lower().find('source("')
     if i > -1:
         s = txt[i : len(txt)]
         #avsp.MsgBox(s, cancel = True)
         a = {}
         a = s.split(sep)
         if len(a) > 1:
            fileName = a[1]
     else:  
         i = txt.lower().find('scriptdir')
         if i > -1:
             s = txt[i : len(txt)]
             a = {}
             a = s.split(sep)
             if len(a) > 1:
                fileName = os.path.join(avsp.GetScriptFilename(propose='general', only='dir'), a[1])

# if source not found, remove the avs ext and hopefully the source have the same name
if not fileName:
   fileName=os.path.splitext(avsp.GetScriptFilename(propose='general'))[0]# remove '.avs'

fileName = fileName.encode(sys.getfilesystemencoding())

if os.path.isfile(fileName): 
     sourceFile = fileName
     fileName = os.path.splitext(fileName)[0]
     if fileName:
        fileName += framenr
else:
    dir=avsp.GetScriptFilename(propose='general', only='dir')
    fn=os.path.splitext(avsp.GetScriptFilename(propose='general', only='base'))[0] + framenr
    if dir:
        dir = dir.encode(sys.getfilesystemencoding())
        fn = fn.encode(sys.getfilesystemencoding())
        if doMessage:
            tx = avsp.GetTextEntry(message=dir, default=fn, title='Enter Filename to save the Image', types='text', width=300)
            if not tx:
                return
        else:
            tx = fn
        fileName = os.path.join(dir, tx)

if fileName:
    if os.path.isfile(fileName + fnExt):
         i = 2
         s = fileName
         while os.path.isfile(s + fnExt):
              s = fileName + ' (' + str(i) + ')'
              i += 1
         fileName = s + fnExt
    else:
         fileName += fnExt
    #fileName=fileName.encode(sys.getfilesystemencoding())

#avsp.MsgBox(fileName, cancel = True)
fileName=avsp.SaveImage(filename=fileName, framenum=None, index=None, default='', quality=jpgQ)

if fileName and sourceFile:
# for other uses
    pass