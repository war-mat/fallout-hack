#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

class Character(object):
    
    def __init__(self, char, screen_y, screen_x, text_y, text_x):
        
        self.char = char
        self.screen_y = screen_y
        self.screen_x = screen_x
        self.text_y = text_y
        self.text_x = text_x

class GameText(object):
    """ 2d array of characters """
    
    def __init__(self, row_start, left_col_start, right_col_start, line_width, 
        num_rows, left_text, right_text):
        
        self.line_width = line_width
        self.num_rows = num_rows
        
        # text up-down bounds (screen coords)
        self.row_start = row_start
        self.row_end = row_start + num_rows
        
        # left text column bounds (screen coords)
        self.left_lower = left_col_start
        self.left_upper = self.left_lower + self.line_width - 1
        
        # right column bounds (screen coords)
        self.right_lower = right_col_start
        self.right_upper = self.right_lower + self.line_width - 1
        
        # pick a random starting memory address
        self.start_address = self.set_start_address()
        
        # generate a list of addresses starting from that
        self.gen_address_list(self.start_address)
        
        self.left_text_block = self.vector_to_2d_array(left_text)
        self.right_text_block = self.vector_to_2d_array(right_text)
        
        self.alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.junk = set("$.':_!\"+-%\/|*@#`=^;?,")
        self.left_brackets = list("([<{")
        self.right_brackets = list(")]>}")
        
        self.right_text_list = []
        self.right_max_lines = 21
        
    def add_right_line(self, string):

        self.right_text_list.insert(0, ('>' + string))
        
        if len(self.right_text_list) > self.right_max_lines:
            
            self.right_text_list.pop()
        
    def is_alpha(self, char):
        
        return char in self.alphabet
        
    def is_junk(self, char):
        
        return char in self.junk
        
    def is_bracket(self, char):
        
        return (char in self.left_brackets or char in self.right_brackets)
        
    def set_start_address(self):
        
        # maximum memory address
        start_address_max = 65535 - (self.line_width * self.num_rows * 2)
        
        # select random address between 0x0000 and max
        return random.randint(0, start_address_max)
        
    def int_address_to_hex_string(self, int_address):
    
        address_str = hex(int_address)[2:].upper()
        
        # pad with leading 0s to give strings of 4 hex digits
        while len(address_str) < 4:
            
            address_str = '0' + address_str
            
        return "0x" + address_str
        
    def gen_address_list(self, start_address):
        
        self.address_list = []
        
        while len(self.address_list) < (self.num_rows * 2):
            
            self.address_list.append(self.int_address_to_hex_string(start_address))
            
            start_address += self.line_width

    def vector_to_2d_array(self, text):
        
        output = []
        
        for i in xrange(self.num_rows):
            
            # indices to split text vector into lines
            start_index = (i * self.line_width)
            end_index = (i * self.line_width) + self.line_width
            
            row = text[start_index:end_index]
            
            #print type(row)
            
            output.append(row)
            
        return output
        
    def translate_cursor_to_block(self, side, cursor_y, cursor_x):
        """ convert cursor (absolute) coords to text block coords """
        
        pos_y = cursor_y - self.row_start
        pos_x = 0
        
        if side == "left":
            pos_x = cursor_x - self.left_lower
        else:
            pos_x = cursor_x - self.right_lower
            
        return pos_y, pos_x
        
    def translate_block_to_cursor(self, side, pos_y, pos_x):
        """ convert text block coords to cursor (absolute) coords """
        
        cursor_y = pos_y + self.row_start
        cursor_x = 0
        
        if side == "left":
            cursor_x = pos_x + self.left_lower
        else:
            cursor_x = pos_x + self.right_lower
            
        return cursor_y, cursor_x
        
    def check_alpha_left(self, side, pos_y, pos_x):

        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
            
        highlight_chars = []

        while True:
                
            pos_x -= 1 # move 1 space left
                
            if pos_x < 0:
                if pos_y > 0:
                    pos_x = self.line_width - 1
                    pos_y -= 1 # move up one
                else:
                    break

            if self.is_alpha(text[pos_y][pos_x]):
                
                char = text[pos_y][pos_x]
                screen_y, screen_x = (self.translate_block_to_cursor(side, 
                    pos_y, pos_x))
                    
                highlight_chars.append(Character(char, screen_y, screen_x, 
                    pos_y, pos_x))
            else:
                break
                
        return highlight_chars
        
    def check_alpha_right(self, side, pos_y, pos_x):
        
        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
        
        highlight_chars = []
        
        while True:
                
            pos_x += 1 # move 1 space right
                
            if pos_x > (self.line_width - 1):
                if pos_y < (self.num_rows - 1):
                    pos_x = 0
                    pos_y += 1 # move down one
                else:
                    break

            if self.is_alpha(text[pos_y][pos_x]):
                
                char = text[pos_y][pos_x]
                screen_y, screen_x = (self.translate_block_to_cursor(side, 
                    pos_y, pos_x))
                    
                highlight_chars.append(Character(char, screen_y, screen_x, 
                    pos_y, pos_x))
            else:
                break
                
        return highlight_chars
        
    def check_bracket_left(self, side, pos_y, pos_x, matching, max_length):
        
        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
        
        found = False
        highlight_chars = []

        while True:
                
            pos_x -= 1 # move 1 space left
                
            if pos_x < 0:
                if pos_y > 0:
                    pos_x = self.line_width - 1
                    pos_y -= 1 # move up one
                else:
                    break
            
            char = text[pos_y][pos_x]
                
            # brackets cannot contain words
            if self.is_alpha(char):
                break
            else:
                screen_y, screen_x = (self.translate_block_to_cursor(side, 
                        pos_y, pos_x))
                        
                highlight_chars.append(Character(char, screen_y, screen_x, 
                        pos_y, pos_x))       
                
                if len(highlight_chars) > max_length - 1:
                    break
                    
                if char == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found
        if not found:
            highlight_chars = []
            
        return highlight_chars
        
    def check_bracket_right(self, side, pos_y, pos_x, matching, max_length):
        
        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
        
        found = False
        highlight_chars = []
        
        while True:
                
            pos_x += 1 # move 1 space right
                
            if pos_x > (self.line_width - 1):
                if pos_y < (self.num_rows - 1):
                    pos_x = 0
                    pos_y += 1 # move down one
                else:
                    break
                
            char = text[pos_y][pos_x]

            # brackets cannot contain words
            if self.is_alpha(char):
                break
            
            else:
                screen_y, screen_x = (self.translate_block_to_cursor(side, 
                        pos_y, pos_x))
                        
                highlight_chars.append(Character(char, screen_y, screen_x, 
                        pos_y, pos_x))
                
                if len(highlight_chars) > max_length - 1:
                    break
                    
                if char == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found            
        if not found:
            highlight_chars = []
        
        return highlight_chars
        
    def get_highlighted(self, side, cursor_y, cursor_x):
        """ 
        Return Character object containing selected characters and their text 
        block and screen coordinates.
        """
        
        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
        
        # convert to text block coords    
        pos_y, pos_x = self.translate_cursor_to_block(side, cursor_y, cursor_x)
        
        # get character at those coords
        char = text[pos_y][pos_x]

        # add that character to highlight list
        hl_list = [Character(char, cursor_y, cursor_x, pos_y, pos_x)]
            
        # check character type (alpha, bracket, junk)
        if self.is_alpha(char):
            
            # check characters to the left and right
            hl_list += self.check_alpha_left(side, pos_y, pos_x)
            hl_list += self.check_alpha_right(side, pos_y, pos_x)
            
        elif self.is_bracket(char):
            
            # find whether matching bracket is left or right
            if char in self.left_brackets:
                matching = self.right_brackets[self.left_brackets.index(char)]
                
                # check characters to the right of current position
                hl_list += self.check_bracket_right(
                        side, pos_y, pos_x, matching, 20)
                
            else:
                matching = self.left_brackets[self.right_brackets.index(char)]
            
                # check characters to the left of current position
                hl_list += self.check_bracket_left(
                        side, pos_y, pos_x, matching, 20)
        
        return hl_list
        
    def delete_word(self, side, highlight_list):
        """ replace specified chars in text block with .s """
        
        if side == "left":
            text = self.left_text_block
        else:
            text = self.right_text_block
            
        for hl in highlight_list:
            
            text[hl.text_y][hl.text_x] = '.'
        
    def get_selected_word(self, highlight_list):
        
        out = ""

        # sort by y, then x
        highlight_list.sort(key=lambda x: (x.text_y, x.text_x))
        
        for hl in highlight_list:
            
            out = out + hl.char
            
        return out

    def is_word(self, highlight_list):
        
        return self.is_alpha(highlight_list[0].char)
        
    def is_bracket_set(self, highlight_list):
        
        return self.is_bracket(highlight_list[0].char) and \
            len(highlight_list) > 1
