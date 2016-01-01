#!/usr/bin/python2
# -*- coding: utf-8 -*-

import curses

import lib.fallout_game as fallout_game

def curses_close(screen):
    
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.curs_set(1)
    curses.endwin()

def curses_setup(screen):
        
    curses.noecho()
    curses.curs_set(0)
    curses.cbreak()
    screen.keypad(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    screen.attrset(curses.color_pair(1))
    screen.border(0)

def main():
    
    # wrap all curses code inside try block to not screw up terminal settings
    # if an error arises
    try:
        # initialize curses
        screen = curses.initscr()
        
        # curses settings
        curses_setup(screen)
        
        # create difficulty levels, here then later from config file
        # or a list of tuples

        game = fallout_game.Game(screen)
        
        level = 0
        max_level = 4 #
        
        while True:
            if level > max_level:
                # game is beaten, display something
                pass
            else:
                game.new_game(level)
                
                if game.play_game() == "win":
                    level += 1
                else:
                    # print you lose or something
                    break

    finally:
        curses_close(screen)

if __name__ == '__main__':

    main()

# unify all Classes to basically operate the same
# take parameters and init, create variables and whatever when a new game is started
# perferably with a similar "new_game" method in each
