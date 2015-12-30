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
        
        # use these to position elements
        window_height, window_width = screen.getmaxyx()
        
        # create difficulty levels, here then later from config file
        # or a list of tuples
        difficulty = {
            0:("word_len", "num_words", "match limit"),
            1:("word_len", "num_words", "match limit")
            }
        
        # constants
        WORD_LENGTH = 7
        NUM_WORDS = 15
        MATCH_LIMIT = 4
        LINE_WIDTH = 15
        NUM_ROWS = 17
        ROW_START = 6
        ROW_END = 22
        LEFT_ADDRESS_START = 1
        RIGHT_ADDRESS_START = LEFT_ADDRESS_START + 7 + LINE_WIDTH + 2
        RIGHT_CURSOR_POS = 49
        RIGHT_LINE_POS = RIGHT_CURSOR_POS + 1
        
        
        game = fallout_game.Game(screen)
        
        game.new_game(NUM_WORDS, MATCH_LIMIT, WORD_LENGTH, LINE_WIDTH, NUM_ROWS)
        
        game.play_game()

    finally:
        curses_close(screen)

if __name__ == '__main__':

    main()

