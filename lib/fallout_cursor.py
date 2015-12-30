#!/usr/bin/python2
# -*- coding: utf-8 -*-

import curses

class Cursor(object):
    
    def __init__(self, screen, initial_y, initial_x, row_start, col_start,
        line_width, num_rows):
        
        self.screen = screen
        
        self.cursor_y = initial_y
        self.cursor_x = initial_x
        
        # move cursor to initial position
        self.update_cursor_pos()
        
        # text column up-down bounds
        self.row_start = row_start
        self.row_end = row_start + num_rows - 1
        
        # text column left-right bounds (screen coords)
        self.left_lower = col_start + 7
        self.left_upper = self.left_lower + line_width - 1
        self.right_lower = self.left_upper + 10
        self.right_upper = self.right_lower + line_width - 1
        
        # which column cursor is currently in
        self.side = self.get_side()
        
    def move_right(self):
        
        self.cursor_x += 1
        
        if self.cursor_x > self.left_upper and self.cursor_x < self.right_lower:
            self.cursor_x = self.right_lower # skip over center
        elif self.cursor_x > self.right_upper:
            self.cursor_x = self.right_upper # set to right edge
            
    def move_left(self):
        
        self.cursor_x -= 1
        
        if self.cursor_x < self.right_lower and self.cursor_x > self.left_upper:
            self.cursor_x = self.left_upper # skip over center
        if self.cursor_x < self.left_lower:
            self.cursor_x = self.left_lower # set to left edge
            
    def move_down(self):
        
        if self.cursor_y < self.row_end:
            self.cursor_y += 1
        
    def move_up(self):
        
        if self.cursor_y > self.row_start:
            self.cursor_y -= 1
        
    def handle_arrow_keys(self, key):
        
        if key == curses.KEY_LEFT:
            self.move_left()
        elif key == curses.KEY_RIGHT:
            self.move_right()
        elif key == curses.KEY_UP:
            self.move_up()
        elif key == curses.KEY_DOWN:
            self.move_down()
        
        # check which column cursor is in
        self.side = self.get_side()
        
        # move cursor to new position
        self.update_cursor_pos()
        
    def set_cursor_pos(self, cursor_y, cursor_x):
        
        self.cursor_y = cursor_y
        self.cursor_x = cursor_x
        
        self.update_cursor_pos()
                
    def update_cursor_pos(self):
        
        self.screen.move(self.cursor_y, self.cursor_x)
        
    def report_cursor_pos(self):
        
        return (self.cursor_y, self.cursor_x)
        
    def get_side(self):
        
        side = ""
        
        if self.cursor_x < self.right_lower:
            side = "left"
        else:
            side = "right"
            
        return side
