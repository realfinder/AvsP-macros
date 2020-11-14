AVSPMOD MACRO API
=================

    AvsP allows you to define your own macros using the Python programming
language.  In order to use this functionality, simply write your own Python
code in a text file and save it in the "macros" directory with the extension
".py".  The next time you start AvsP.exe, your macro will appear in the
"Macros" menu (the macros are sorted alphabetically).  The extension and
any initial open-close brackets are removed in the displayed name - the file
"[001] My Macro.py" shows up in the menu as "My Macro", in order to help
order the macros in the menu.  If the striped name is empty, the first line
from the script is used as the display name, removing '#' if present.
Separators can be inserted in the menu by creating empty macro files with
name "[001] ---.py".  To help further organize your macros, you can put
macros in any subdirectories you create in the "macros" folder, which will
automatically create submenus in the "Macros" menu.

    Macro files can also be used to add options to the macro menu that can
be read by any macro through the IsMenuChecked macro function.  To include
a check option, create an empty macro and prefix its name with "ccc", e.g.
"[001] ccc option name.py".  To add exclusive choices, create a macro for
each option with the prefix "rrr".

    Macros can optionally run in its own thread if the script includes a
commentary line like "# run macro in new thread" (without quotes).  This
makes possible to wait for the end of external commands started from the
macro without locking AvsPmod.

    You need to have a pretty good understanding of Python to write your own
macros (plenty of documentation and tutorials for Python can be found on the
web).  Several examples are provided in the "macros" directory to show basic
usage, many more things are possible.  The following is a description of the
functions provided in the local module avsp to give you control over the
program itself (see the examples for appropriate usage).  This information
can also be retrieved from the module or functions' docstring (help(avsp) or
help(avsp.FunctionName)).


InsertText(txt, pos=-1, index=None)
===================================

Inserts the string 'txt' into the script of the tab located at the zero-based
integer 'index' at the text position 'pos'.

If the input 'index' is None, the text is inserted into the script of the
currently selected tab.  The input 'pos' can be either an integer representing
the zero-based position in the text document (a value of -1 is equivalent
to the last position) or a tuple representing the zero-based line and column
numbers (a value of -1 is equivalent to the last line or column, respectively).
Alternatively, if 'pos' is equal to None, the text is inserted at the current
cursor position in the document, replacing any existing selection.  In all
cases, the cursor is positioned at the end of the inserted text.

Returns False if insert failed (due to bad inputs), True otherwise.


SetText(txt, index=None)
========================

Similar to InsertText, but replaces all the text in the script of the tab
located at the zero-based integer 'index' with the string 'txt'.  If the
input 'index' is None, the text is inserted into the script of the currently
selected tab.  Returns False if the operation failed, True otherwise.


GetText(index=None, clean=False)
================================

Returns the string containing all the text in the script of the tab located
at the zero-based integer 'index'.  If the input 'index' is None, the text
is retrieved from the script of the currently selected tab.  If 'clean' is
True, strip sliders and tags from the returned text.  Returns False
if the operation failed.


GetSelectedText(index=None)
===========================

Similar to GetText(), but returns only the selected text.


GetSourceString(filename='', default='')
========================================

Returns an appropriate source string based on the file extension of the input
string 'filename'.  For example, if 'filename' is "D:\test.avi", the function
returns the string "AviSource("D:\test.avi")".  Any unknown extension is wrapped
with "DirectShowSource(____)" (AviSynth) or "FFVideoSource(____)" (AvxSynth).
Templates can be viewed and defined in the options menu of the program.

If 'filename' is empty, the user is prompted to select a file from a dialog box
with 'default' as the default filename; it can be just a directory or basename.


GetSourceStringFromFilename(filename)
=====================================
Returns an appropriate source string based on the file extension of the input
does not check if the file exists. see GetSourceString.

GetPluginString(filename='', default='')
========================================

Returns an appropriate load plugin string based on the file extension of the
input string 'filename'.  For example, if 'filename' is "D:\plugin.dll", the
function returns the string "LoadPlugin("D:\plugin.dll")".  VirtualDub and
VFAPI (TMPGEnc) plugins are also supported.

If 'filename' is empty, the user is prompted to select a file with a dialog
box, always started on the last directory from which a plugin was loaded for
easy selection and with 'default' as the default filename; it can be just a
directory or basename.


GetFilename(title='Open a script or source', filefilter=None, default='')
=========================================================================

Displays an open file dialog box, returning the filename of the selected file
if the user clicked "OK", returning an empty string otherwise.  filefilter=None
means to apply those extensions defined at "Options|Extension templates".
'default' is the default filename set in the dialog box; it can be just a
directory or basename.


GetSaveFilename(title='Save as', filefilter=_('All files') + ' (*.*)|*.*', default='')
======================================================================================

Displays an save file dialog box, returning the entered filename if the user
clicked "OK", returning an empty string otherwise.  'default' is the default
filename set in the dialog box; it can be just a directory or basename.


GetDirectory(title='Select a directory')
========================================

Displays a dialog box to select a directory, returning the name of the
selected directory if the user clicked "OK", returning an empty string
otherwise.  'default' is the dialog's starting directory.


GetTextEntry(message='', default='', title='Enter information', types='text', width=400)
========================================================================================

Multiple entry dialog box.  In its more simple form displays a dialog box with
the string 'message' along with a field for text entry, initially filled with
the string 'default', returning the string from the text entry field if the
user clicked "OK", an empty string otherwise.

title: title of the dialog box.

The 'message', 'default' and 'types' parameters are list of lists.  If a list
were to contain only one component then it's not mandatory to wrap it as list.

message: list of the lines of the dialog box, in which every component is a
list of the corresponding text strings to the entries in that line.  There must
be as many strings as desired entries.

default: list of lists holding tuples with the default values for each entry.
In the same way as lists, if a tuple were to contain only one element then
it's not necessary to wrap it.  Each tuple and the whole parameter are optional
except for list entry type.

types: list of lists containing the types of each entry.  Each value and the
whole parameter are optional.  Every omitted entry type defaults to a regular
text field.

Types available:

- 'text': regular text field.
  'default' values: 1-tuple with the initial field text.

- 'file_open': text field with additional browse for file button ("open"
      dialog).
  'default' values: 1-tuple or 2-tuple, with the initial field text and an
      optional file wildcard with this syntax:
      "BMP files (*.bmp)|*.bmp|GIF files (*.gif)|*.gif"

- 'file_save': same as 'file_open', but with a "save" dialog.

- 'dir': text field with additional browse for directory button.
  'default' values: 1-tuple with the initial field text.

- 'list_read_only': drop-down list.  The 'default' tuple is mandatory.
  'default' values: n+1 tuple, where the first n elements are the strings
      than compose the list and the last one is the entry selected by default.

- 'list_writable': same as above but with the text field direcly writable, so
      the return value is not limited to a selection from the list.

- 'check': simple check box, returning True if checked.
  'default' values: 1-tuple with the predetermined boolean value, False as
      default.

- 'spin': numeric entry, with arrows to increment and decrement the value.
  'default' values: up-to-5-tuple, containing the default, minimum, maximum,
      decimal digits shown and increment when using the arrows. With zero
      decimal digits returns int, float otherwise.
      Default: (0, None, None, 0, 1)

- 'slider_h': horizontal slider. Similar to 'spin', but with a draggable handle.
  'default' values: up-to-4-tuple containing the default, minimum, maximum and
      space between ticks marks that can be displayed alongside the slider.
      Default: (50, 0, 100, no ticks)

- 'slider_v': vertical slider, same as above.

- 'sep': separator formed by a text string and a horizontal line.
  'default' values: 1-tuple with an optional fixed line length (by default
      it extends through all the dialog's width).  Set it to -1 to auto-adjust
      to the text length.  Note that an invisible separator can be created by
      setting 'message' to '' and 'default' to 0 or -1.  To include the 'default'
      parameter but don't give a fixed length (e.g. there's more entries
      following that one) set the tuple to None or any not-convertible-to-int
      value, like ''.

A not recognized type string, including '', defaults to 'text' type.

width: minimal horizontal length of the dialog box.  The width is distributed
uniformly between the entries in each line.

Return values: list of entered values if the user clicks "OK", empty list
otherwise.


WriteToScrap(txt, pos=-1)
=========================

This function is identical to InsertText, except that instead of writing to
one of the existing tabs, it writes to a scrap window (which is always on top,
making it useful to keep track of the text as it changes).  Any inserted text
is highlighted temporarily.


GetScrapText()
==============

Identical to the GetText function, except that it retrieves all text from the
scrap window.


NewTab(copyselected=True)
=========================

Creates a new tab (automatically named "New File (x)", where x is an appropriate
integer).  If any text was selected in the most recent tab and 'copyselected' is
True, it is automatically copied over to the new tab's text.


CloseTab(index=None, prompt=False, discard=False)
=================================================

Closes the tab at integer 'index', where an index of 0 indicates the first
tab. If 'index' is None (the default), the function will close the currently
selected tab.

If the argument 'discard' is True any unsaved changes are lost.  Otherwise,
if 'prompt' is True the program will prompt the user with a dialog box to
save the file if there are any unsaved changes.  If 'prompt' is False, the
function will not prompt the user and will close the script only saving
changes on scripts that already exist on the filesytem.


SelectTab(index=None, inc=0)
============================

Selects the tab located at the integer 'index', where an index of 0 indicates
the first tab.  If the 'index' is None, the integer 'inc' is used instead
to determine which tab to select, where inc is an offset from the currently
selected tab (negative values for inc are allowable).  Returns False upon
failure (invalid input), True otherwise.


GetTabCount()
=============

Returns the number of scripts currently open.


GetCurrentTabIndex()
====================

Returns the zero-based index of the currently selected tab.


GetScriptFilename(index=None, propose=None, only=None)
======================================================

Returns the name of the script at the tab located at the integer 'index',
where an index of 0 indicates the first tab.  If 'index' is None, the
currently selected tab is used.  The returned name is the filename of the
script on the hard drive.  If the script has never been saved to the hard
drive, the returned name is an empty string.

If 'propose' is set, return a proposed save filepath for the script based
on its filename, tab's title, first source in the script and user preferences.
This path can be useful to open/save other files.  Posible 'propose' values:
'general', 'image'.  If 'only' is set to 'dir' or 'base', return only the
directory or basename respectively.

OpenFile(filename='', default='')
=================================

If the string 'filename' is a path to an Avisynth script, this function opens
the script into a new tab.  If 'filename' is a path to a non-script file, the
filename is inserted as a source (see the GetSourceString function for details).

If 'filename' is not supplied, the user is prompted with an Open File dialog
box with 'default' as the default filename; it can be just a directory or
basename.


SaveScript(filename='', index=None, default='')
===============================================

Saves all the unsaved changes of the script in the tab located at the integer
'index'.  If 'index' is None, the script in the currently selected tab is used.

The function will prompt the user with a dialog box for the location to save
the file if the string 'filename' is not provided and the script does not
already exist on the hard drive, using 'default' as the default filename;
it can be just a directory or basename.

If a file with the same name as 'filename' already exists, it is overwritten
without any prompting.  The function returns the filename of the saved file.


SaveScriptAs(filename='', index=None, default='')
=================================================

Similar to the function SaveScript(), except that if the filename is an empty
string, this function will always prompt the user with a dialog box for the
location to save the file, regardless of whether or not the script exists on
the hard drive.


IsScriptSaved(index=None)
=========================

Returns a boolean indicating whether the script in the tab located at the
integer 'index' has any unsaved changes.  If 'index' is None, the script in
the currently selected tab is used.  Returns False if there are any unsaved
changes, True otherwise.


RenameScript(new_title, index=None)
===================================

Renames the tab located at the integer 'index' to 'new_title'.  If 'index' is
None, then the currently selected tab is used.

If the script was saved to the filesystem the file is renamed as well.  Returns
False if the file couldn't be renamed, True otherwise.


ShowVideoFrame(framenum=None, index=None, forceRefresh=False)
=============================================================

This function refreshes the video preview (unhiding it if it is hidden) using
the frame specified by the integer 'framenum', using the script of the tab
located at the integer 'index'.  The function also automatically selects the
tab located at 'index'.

If 'framenum' is None, it uses the current frame number from the video preview
slider.  If 'index' is None, the frame of the currently selected tab is shown.
If the input 'forceRefresh' equals True, then the script is reloaded before
showing the video frame (normally the script is reloaded only when the text
has changed).


ShowVideoOffset(offset=0, units='frames', index=None)
=====================================================

Similar to ShowVideoFrame(), except the user specifies an offset instead of
the direct frame.  Offset can be positive or negative (for backwards jumping).
The string argument 'units' specifies the units of the offset, and can be either
'frames', 'seconds', 'minutes', or 'hours'.


UpdateVideo(index=None)
=======================

This function is similar to ShowVideoFrame(), but does not force the video
preview to be shown if it is hidden.


HideVideoWindow()
=================

Hides the video preview window if it is visible (note that the video controls
are always visible).


GetFrameNumber()
================

Returns the current integer frame number of the video preview slider.


GetVideoWidth(index=None)
=========================

Returns the width of the video of the script at the tab integer 'index'.  If
'index' is None, then the currently selected tab is used.


GetVideoHeight(index=None)
==========================

Returns the height of the video of the script at the tab integer 'index'.  If
'index' is None, then the currently selected tab is used.


GetVideoFramerate(index=None)
=============================

Returns the framerate of the video of the script at the tab integer 'index'.
If 'index' is None, then the currently selected tab is used.


GetVideoFramecount(index=None)
==============================

Returns the framecount of the video of the script at the tab integer 'index'.
If 'index' is None, then the currently selected tab is used.


GetPixelInfo(color='hex', wait=False, lines=False)
==================================================

Waits for the user to left-click in a position of the video preview, showing
it if hidden, and returns a tuple with the position and colour of the clicked
pixel.  The colour representation can be specified with the 'color' parameter.
Valid values: 'hex', 'rgb', 'rgba', 'yuv', None.  If None, only returns the
position.

The position is counted from the top left corner.  If the user clicks on a
part of the preview outside the video, the returned coordinates are set to
the nearest video pixel and the colour to None.

If the user doesn't click the video within the first 5 seconds after the
preview is refreshed, returns None.

If 'wait' is True waits for multiple clicks with a 5 seconds time-out between
each one and returns a list with the pixel data, empty list if not pixel was
clicked.  Lines are marked over the video preview if 'lines' is True.


GetVar(var, index=None)
=======================

Returns the content of the avisynth variable 'var' at the tab integer 'index'.
If 'index' is None, then the currently selected tab is used.  Returns None if
the specified variable is not defined.

Warning: If the variable is frame-dependent the returned value may be unreliable.
Two conditions must be met to ensure that is correct:
- Avisynth frame cache must be disabled, e.g. SetMemoryMax(1)
- No filters that request multiple frames can be used in the script.


RunExternalPlayer(executable=None, args='', index=None)
=======================================================

Runs the external program specified by the string argument 'executable'.

The first argument passed to the program is the filename of the preview script
generated from the script located at the tab integer 'index'.  If 'index' is
None, then the currently selected tab is used.  Additional arguments can be
passed to the external program using the string parameter 'args'.

If the specified executable does not exist, then the function returns False,
otherwise it runs the executable program with the appropriate arguments and
returns True.


Pipe(cmd, text=None, frames=None, y4m=False, reorder_rgb=False, wait=False, callback=None, stdout=None, stderr=None)
====================================================================================================================

Pipe raw frame data to an external application (video only)

cmd: right side of the pipe (Unicode string). Accepts several variables:
     {height}, {width}, {fps}, {frame_count}.
text : script evaluated.  Defaults to the script in the current tab.  It
       can also be a path to an AviSynth script.
frames: sequence of frames to send.  Defaults to the complete frame range
        of the evaluated text.
y4m: add a yuv4mpeg2 header.  It can be a logical value or optionally a
     dict with some of the following keys:
     - colorspace: overrides the clip colorspace.
     - depth: for >8 bits per channel. It's appended to 'colorspace'.
     - width, height: may be necessary when piping fake data. It can be
       either an int or a modifier '[x*/]\d+', e.g. 'width':'/2' will
       signal half the width of the evaluated clip.
     - sar: 'X:Y' string.
     - X_stream, X_frame.
reorder_rgb: convert BGR to RGB and BGRA to RGBA before piping.
wait: wait for the process to finish.  If False, return the Popen object.
      If True, return a tuple (Popen object, return code).  The return code
      is 1 if the user cancels.
callback: user function called before each frame is sent and after all frames
          are piped.  It receives three arguments, number of the current frame
          in the sequence, number of the current frame in the clip and total
          frame count, and must return True to keep piping, False to cancel.
stdout: file object where redirect stdout.  Defaults to sys.stdout on __debug__,
        nowhere otherwise.
stderr: file object where redirect stderr.  Defaults to stdout.


SaveImage(filename='', framenum=None, index=None, default='', quality=None, depth=8)
====================================================================================

Saves the video frame specified by the integer 'framenum' as a file specified
by the string 'filename', where the video corresponds with the script at the
tab integer 'index'.

If 'filename' is an empty string, then the user is prompted with a dialog box
with 'default' as the default filename; it can be just a directory or basename.
If 'index' is None, then the currently selected tab is used.

A quality level (0-100) can be specified for JPEG output. If the quality is
not specified, it gets prompted from a dialog window.

The image can be saved as RGB48 if 'depth' is 16 and the ouptut format PNG.
In this case it's assumed that the script returns a fake clip double the real
height.

Returns the choosen filename if the image was saved, None otherwise.


GetBookmarkList(title=False)
============================

Returns a list containing the video frame bookmarks currently set by the
user.  Note that these are the standard frame bookmarks, and do not contain
any selection startpoints or endpoints which may exist. If 'title' is True,
returns a list of tuple (frame, title).


SetBookmark(input)
==================

Toggle 'input' as a video frame bookmark.  If 'input' is a list, toggle each
of its values as a video frame bookmark.  Each bookmark can be a single integer
or a tuple (frame , title).  Returns True if successful, False otherwise.


ClearBookmarks(start=0, end=None, clear_current=True, clear_historic=False)
===========================================================================

Clear all video frame bookmarks in the range [start, end], optionally
deleting also historic bookmarks.


GetSelectionList()
==================

Returns a list containing the video frame selections created by AvsP's trim
selection editor, where each element of the list is a 2-element tuple containing
the startpoint and the endpoint of a selection.  Note that the trim selection
editor must be visible for any selections to exist.


MsgBox(message, title='', cancel=False)
=======================================

Displays a simple dialog box with the text string 'message' and title 'title',
and an additional cancel button if 'cancel' is True.  Returns True if the user
presses 'OK' and the cancel button is present, or always True if it's not.


ProgressBox(max=100, message='', title='Progress')
==================================================

Returns a wxPython dialog control which displays the progress of any given
task as a fraction of the input integer 'max'.

In order to display the dialog, use its method Update(value, message), which
takes in the new progress value and optionally a new message.  The method
Update returns a tuple where its first component is False if the user clicked
on the Cancel button, True otherwise.  Wrap this method with SafeCall if it's
called within a thread.

IMPORTANT: You must use the Destroy() method to destroy the dialog after you
are done with it.


GetSliderInfo(index=None)
=========================

Returns a list containing information for each slider in the script located
at the tab integer 'index'.  If 'index' is None, then the currently selected
tab is used.

The slider information consists of 4 items.  The first item is the slider text
itself.  The second item is the slider label.  The third item is the list of
numbers which the graphical slider represents.  The fourth item is the number
of decimal places for the slider numbers as specified by the user.


ExecuteMenuCommand(text, callafter=False)
=========================================

Executes one of AvsP's menu commands as specified by the input 'text', which
can either be the name of the menu command or the keyboard shortcut.

For example, you can create a new tab in a macro by using either
"avsp.ExecuteMenuCommand('File -> New Tab')" or by using
"avsp.ExecuteMenuCommand('Ctrl+N')".  In this manner all menu commands are
available to AvsP's macro language.  The input text is not case sensitive,
but must be spelled precisely in order to work (a complete list of all the
commands and shortcuts with precise spelling can be found in the
"Options -> Configure shortcuts..." dialog).  If callafter=True, the menu
command will run after the current macro has exited.

Returns True if successful, False otherwise.


IsMenuChecked(text)
===================

Retrieve the state of a menu item under Macros menu. The parameter 'text' has
the same meaning as that one of ExecuteMenuCommand function.


GetWindow()
===========

Get the handler of AvsP's main window.  Don't use this except you know what
you are doing.


SafeCall(callable [, param1, ...])
==================================

Run the function or method specified in a thread-safe way.  This wrapper is
usually necessary when the code is run from a thread and the callable is not
part of the macro API and interacts with the GUI:
- Update method of ProgressBox
- Resources obtained through GetWindow
- Other wxPython resources obtained through importing wx.



** VARIABLES **


Version
=======

Dictionary containing version info.  Keys:
[AvsP, AviSynth_string, AviSynth_number, AviSynth_interface]


Options
=======

This dictionary can be used to store persistent data.  Each macro have its 
own dictionary.


Last
====

This variable contains the return value of the latest executed macro.  It is 
useful to create reusable macros.
