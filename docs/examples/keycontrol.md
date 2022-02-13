
# Keyboard Control

The default keyboard controller is implemented using the
[``keyboard``](https://pypi.org/project/keyboard/) package. This makes it 
cross-platform, but the package is not without its quirks; it installs a 
global listner for your keyboard, meaning it picks up key presses even if its
window is not in focus. This can cause issues if the keyboard controller is
looping but you switch contexts, perhaps to a browser, to perform a search,
and inadverdently begin moving the stage around. Be cautious!

``` python
from autogator.api import load_default_configuration
from autogator.controllers import KeyboardControl, KeyloopKeyboardBindings

stage = load_default_configuration().get_stage()

kc = KeyboardControl(stage, KeyloopKeyboardBindings())
kc.loop()
```

The default KeyboardControl object has functionality for both continuous motion
as well as jogged motion. To see the full list of keyboard commands, type "h".
