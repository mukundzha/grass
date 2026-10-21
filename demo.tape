# Regenerate docs/demo.gif with: vhs demo.tape
Output docs/demo.gif

Set Shell "bash"
Set FontSize 20
Set FontFamily "JetBrainsMono Nerd Font"
Set Width 1000
Set Height 600
Set Padding 16
Set Margin 24
Set MarginFill "#1e1e20"
Set WindowBar Colorful
Set WindowBarSize 36
Set BorderRadius 14
Set Framerate 20
Set TypingSpeed 50ms
Set Theme "OneDark"

Hide
Type "mkdir -p /tmp/grass_demo"
Enter
Type "cd /tmp/grass_demo"
Enter
Type "rm -f hello.py"
Enter
Type "touch hello.py"
Enter
Type "PS1='$ '"
Enter
Type "clear"
Enter
Show

Sleep 400ms
Type "grass hello.py"
Enter
Sleep 2300ms
Type "print('hello world')"
Enter
Sleep 500ms
Ctrl+S
Sleep 2s
