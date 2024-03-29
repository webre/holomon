# Holomon
This is a pokemon-style game framework I created as my final project CMU's CS 15-112 class in Summer 2015.

[See here for a video demonstration](https://youtu.be/ksouCLRJjFU) of the sample game setup included in this repo.

This program will only work in Python 3.x.

This program requires __pygame__ to run. Please install pygame [here](https://www.pygame.org/) before running this program.
As of November 2022, pygame is difficult to install on macOS; program was tested on a Windows machine.

This program includes and uses __EzText__, a pygame extension that allows for easy text input and can be found [here](http://www.pygame.org/project-EzText-920-.html) (no need to install this; it is included in the repo).

## Instructions
Move with __W__ __A__ __S__ __D__. Use __E__ to interact with people or objects.

Open the menu with __ESC__. Dismiss text prompts with __ENTER__.

Use the mouse to click menu items and battle options.

Walk across directional arrows to enter different maps. Walking in tall grass may lead to encounters with wild Holomon, and walking into a trainer's line of sight will trigger a battle.

## Config files
This is a *framework* for a pokemon-style game, so it is fully extensible in whichever way you see fit. The included files are simply a sample that demonstrates some core features of the game. The \*.dat files and image files that are placed in the designated folders define the game's entire functionality outside of its basic structure.
