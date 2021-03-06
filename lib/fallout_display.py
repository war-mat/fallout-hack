#!/usr/bin/python2
# -*- coding: utf-8 -*-

import curses
import time

class Display(object):
    
    def __init__(self, screen, line_width, num_rows):

        self.screen = screen
        
        self.line_width = line_width
        self.num_rows = num_rows
        
        # screen coords of right text box
        self.right_text_row = 20
        self.right_text_col = 49
        
        self.right_text_len = 28
        
    def print_char_delay(self, char, row, col, delay):
        
        self.screen.addch(row, col, char)
        
        if delay > 0:
            self.screen.refresh()
            time.sleep(delay / 1000.0)
        else:
            self.screen.refresh()
    
    def print_str_delay(self, string, row, col, string_delay, char_delay):
        
        for i in xrange(len(string)):
            
            self.print_char_delay(string[i], row, col + i, char_delay)
            
        if string_delay > 0:
            self.screen.refresh()
            time.sleep(string_delay / 1000.0)
        else:
            self.screen.refresh()
            
    def print_attempts_left(self, attempts, row, col):
    
        for _ in xrange(4):
            
            if attempts > 0:
                self.screen.addch(row, col, curses.ACS_DIAMOND)
            else:
                self.screen.addch(row, col, ' ')
                
            col += 2
            attempts -= 1

    def print_game_text(self, first_col, first_row, left_text, right_text,
        address_list):
        
        for i in xrange(self.num_rows):
            
            # concatenate address i, left str i, address i+num_rows, right str i
            row_string = address_list[i] + " " + \
                "".join(left_text[i]) + "  " + \
                address_list[(i + self.num_rows)] + " " + \
                "".join(right_text[i])
            
            # print resulting line with delay at end                    
            self.print_str_delay(row_string, (first_row + i), first_col, 50, 0)
            
    def text_block_update(self, first_row, left_text, right_text, 
        left_col, right_col):
        
        for i in xrange(self.num_rows):
            
            left_str = "".join(left_text[i])
            right_str = "".join(right_text[i])
            
            self.print_str_delay(left_str, (first_row + i), left_col, 0, 0)
            self.print_str_delay(right_str, (first_row + i), right_col, 0, 0)
            
        self.screen.refresh()

    def highlight(self, highlight_list, on):
        
        for hl in highlight_list:
            
            if on:
                self.screen.chgat(hl.screen_y, hl.screen_x, 1, curses.A_REVERSE)
            else:
                self.screen.chgat(hl.screen_y, hl.screen_x, 1, curses.A_NORMAL)
            
        self.screen.refresh()
        
    def print_right(self, string, string_delay, char_delay):
        
        erase = " " * self.right_text_len
        
        self.print_str_delay(erase, 22, self.right_text_col, 0, 0)
        
        string = '>' + string
        
        self.print_str_delay(
                string, 22, self.right_text_col, string_delay, char_delay)
        
    def erase_right_text(self):
        
        start = self.right_text_row
        string = " " * self.right_text_len
        
        while start > 0:
            
            # change this to curses' addstr() to avoid per-char overhead
            self.print_str_delay(string, start, self.right_text_col, 0, 0)
            start -= 1
            
    def print_right_text_list(self, text_list):
        
        start = self.right_text_row
        
        for i in xrange(len(text_list)):
            
            string = text_list[i]
            
            self.print_str_delay(string, start, self.right_text_col, 0, 0)
            start -= 1
            
    def clear_all(self):
        
        erase = " " * 78
        
        for i in xrange(1, 23):
        
            self.screen.addstr(i, 1, erase)
        

# separate per-string and per-char delays
