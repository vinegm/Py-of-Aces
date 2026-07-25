# A seeded game for the README: a split, a double down and a hit

Output assets/demo.gif

Set Shell bash
Set FontSize 14
Set Width 820
Set Height 1000
Set Padding 20
Set TypingSpeed 100ms
Set Theme "TokyoNight"

Hide
Type "uv run pyaces --no-config --seed demo34119"
Enter
Sleep 2s
Show

# Normal mode, betting the default $100
Sleep 1.5s
Enter
Sleep 1.5s
Enter
Sleep 2.5s

# A pair: split it, then stand on both hands
Type "p"
Sleep 2s
Space
Sleep 1.5s
Space
Sleep 6s

# Next round: double down on the 10 or 11
Enter
Sleep 1.5s
Enter
Sleep 2.5s
Type "d"
Sleep 6s

# Next round: hit once, then stand
Enter
Sleep 1.5s
Enter
Sleep 2.5s
Type "h"
Sleep 2s
Space
Sleep 10s

Hide
Type "q"
Sleep 300ms
Type "q"
Sleep 300ms
Type "q"
