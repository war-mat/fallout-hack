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
                
            if pos_x < 0 and pos_y > 0:
                pos_x = self.line_width - 1
                pos_y -= 1 # move up one

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
                
            if pos_x > (self.line_width - 1) and pos_y < self.row_end:
                pos_x = 0
                pos_y += 1 # move down one

            if self.is_alpha(text[pos_y][pos_x]):
                
                char = text[pos_y][pos_x]
                screen_y, screen_x = (self.translate_block_to_cursor(side, 
                    pos_y, pos_x))
                    
                highlight_chars.append(Character(char, screen_y, screen_x, 
                    pos_y, pos_x))
            else:
                break
                
        return highlight_chars
        
    def check_bracket_left(self, pos_y, pos_x, matching):
        
        highlight_chars = []
        found = False

        while True:
                
            pos_x -= 1 # move 1 space left
                
            if pos_x < self.left_lower:
                if pos_y > 0:
                    pos_x = self.left_upper
                    pos_y -= 1 # move up one
            elif pos_x < self.right_lower and pos_x > self.left_upper:
                if pos_y > 0:
                    pos_x = self.right_upper
                    pos_y -= 1 # move up one

            # brackets cannot contain words
            if self.is_alpha(self.text_block[pos_y][pos_x]):
                break
            
            else:
                highlight_chars.append(self.translate_block_to_cursor(pos_y,
                    pos_x))
                    
                if self.text_block[pos_y][pos_x] == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found
        if not found:
            highlight_chars = []

        return (found, highlight_chars)
        
    def check_bracket_right(self, pos_y, pos_x, matching):
        
        highlight_chars = []
        found = False
        
        while True:
                
            pos_x += 1 # move 1 space right
                
            if pos_x > self.left_upper and pos_x < self.right_lower:
                if pos_y < self.num_rows-1:
                    pos_x = self.left_lower
                    pos_y += 1 # move down one
            elif pos_x > self.right_upper:
                if pos_y < self.num_rows-1:
                    pos_x = self.right_lower
                    pos_y += 1 # move down one

            # brackets cannot contain words
            if self.is_alpha(self.text_block[pos_y][pos_x]):
                break
            
            else:
                highlight_chars.append(self.translate_block_to_cursor(pos_y,
                    pos_x))
                    
                if self.text_block[pos_y][pos_x] == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found
        if not found:
            highlight_chars = []

        return (found, highlight_chars)
        
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
        
        selected = Character(text[pos_y][pos_x], cursor_y, cursor_x, pos_y, 
            pos_x)
        
        hl_list = [selected]
            
        # check character type
        if self.is_alpha(text[pos_y][pos_x]): # is part of a word
            
            # check characters to the left
            hl_list += self.check_alpha_left(side, pos_y, pos_x)
            # check characters to the right
            hl_list += self.check_alpha_right(side, pos_y, pos_x)
        
        return hl_list
    
        
    '''
        highlight_chars = [(cursor_y, cursor_x)]
        
        hl_type = "junk"
        
        init_y, init_x = self.translate_cursor_to_block(cursor_y, cursor_x)
        
        if self.is_alpha(self.text_block[init_y][init_x]):
            # current character is alphabetical
            
            hl_type = "word"
            
            # check characters to the left of current position
            highlight_chars += self.check_alpha_left(init_y, init_x)
            
            # check characters to the right of current position
            highlight_chars += self.check_alpha_right(init_y, init_x)
            
        elif self.is_bracket(self.text_block[init_y][init_x]):
            # current character is an opening or closing bracket
            
            # find matching bracket
            bracket = self.text_block[init_y][init_x]
            
            if bracket in self.left_brackets:
                matching = self.right_brackets[self.left_brackets.index(bracket)]
                
                # check characters to the right of current position
                results = self.check_bracket_right(init_y, init_x, matching)
                found = results[0]
                highlight_chars += results[1]
            
            else:
                matching = self.left_brackets[self.right_brackets.index(bracket)]
            
                # check characters to the left of current position
                results = self.check_bracket_left(init_y, init_x, matching)
                found = results[0]
                highlight_chars += results[1]
            
            # only if closing bracket is found
            if found:
                hl_type = "bracket"
                
        return highlight_chars, hl_type
    '''
        
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
