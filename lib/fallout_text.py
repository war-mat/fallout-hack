#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

class Character(object):
    
    def __init__(self, char, screen_y, screen_x):
        
        self.char = char
        self.screen_y = screen_y
        self.screen_x = screen_x

class GameText(object):
    """ 2d array of characters """
    
    def __init__(self, row_start, left_col_start, right_col_start, line_width, 
        num_rows):
        
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
        
        # original text strings for searching
        self.left_text = ""
        self.right_text = ""
        
        self.left_text_block = []
        self.right_text_block = []
        
        self.alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.junk = set("$.':_!\"+-%\/|*@#`=^;?,")
        self.left_brackets = list("([<{")
        self.right_brackets = list(")]>}")
        
        self.right_text_list = []
        self.right_max_lines = 20
        
        self.max_bracket_len = 20
        
    def reset_text_list(self):
        
        self.right_text_list = []
        
    def add_right_line(self, string):

        self.right_text_list.insert(0, ('>' + string))
        
        while len(self.right_text_list) > self.right_max_lines:
            
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

    def string_to_2d_array(self, text):
        
        output = []
        
        for i in xrange(self.num_rows):
            
            # indices to split text into into lines
            start_index = (i * self.line_width)
            end_index = (i * self.line_width) + self.line_width
            
            row = list(text[start_index:end_index])
            
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
        
    def check_alpha_left(self, side, index):

        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
            
        hl_list = []

        while True:
            
            index -= 1 # move one character left
            
            if index < 0:
                break
            else:
                char = text[index]
                
                if self.is_alpha(char):
                    screen_y, screen_x = \
                            self.string_index_to_screen_coords(side, index)
                    
                    hl_list.append(Character(char, screen_y, screen_x))
                    
                else:
                    break
        
        # reverse highlight list to put characters in correct order            
        if hl_list:
            hl_list.reverse()
            
        return hl_list
        
    def check_alpha_right(self, side, index):
        
        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
        
        hl_list = []
        
        while True:
                
            index += 1 # move one character right
                
            if index > (len(text) - 1):
                break
            else:
                char = text[index]

            if self.is_alpha(char):
                
                screen_y, screen_x = \
                        self.string_index_to_screen_coords(side, index)
                        
                hl_list.append(Character(char, screen_y, screen_x))
            else:
                break
                
        return hl_list
        
    def check_bracket_left(self, side, index, matching):
        
        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
        
        found = False
        hl_list = []

        while True:
                
            index -= 1 # move one character left
            
            if index < 0:
                break
            else:
                char = text[index]
                
                if self.is_alpha(char):
                    break
                
                screen_y, screen_x = self.string_index_to_screen_coords(
                        side, index)
                        
                hl_list.append(Character(char, screen_y, screen_x))
                
                if len(hl_list) > (self.max_bracket_len - 1):
                    break
                
                if char == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found
        if not found:
            hl_list = []
        else:
            # reverse highlight list to put characters in correct order
            hl_list.reverse()
            
        return hl_list
        
    def check_bracket_right(self, side, index, matching):
        
        # maybe avoid performing this check every time just by passing 'text'
        # itself as an argument to all these functions
        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
        
        found = False
        hl_list = []
        
        while True:
            
            index += 1 # move one character right
            
            if index > (len(text) - 1):
                break
            else:
                char = text[index]
                
                if self.is_alpha(char):
                    break
                
                screen_y, screen_x = self.string_index_to_screen_coords(
                        side, index)
                        
                hl_list.append(Character(char, screen_y, screen_x))
                
                if len(hl_list) > (self.max_bracket_len - 1):
                    break
                
                if char == matching:
                    found = True
                    break
        
        # revert highlight character list if no match found          
        if not found:
            hl_list = []
           
        return hl_list
        
    def get_highlighted(self, side, cursor_y, cursor_x):
        """ 
        Return Character object containing selected characters and their text 
        block and screen coordinates.
        """
        
        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
        
        # convert screen coords to string coords
        index = self.screen_coords_to_string_index(side, cursor_y, cursor_x)
        
        # get character at that string index
        char = text[index]

        # add that character to highlight list
        hl_list = [Character(char, cursor_y, cursor_x)]
        
        # check character type (alpha, bracket, junk)
        if self.is_alpha(char):
            
            # check characters to the left and right
            hl_list = self.check_alpha_left(side, index) + hl_list
            hl_list += self.check_alpha_right(side, index)
        
        elif self.is_bracket(char):
            
            # find whether matching bracket is left or right
            if char in self.left_brackets:
                matching = self.right_brackets[self.left_brackets.index(char)]
                
                # check characters to the right of current position
                hl_list += self.check_bracket_right(side, index, matching)
                
            else:
                matching = self.left_brackets[self.right_brackets.index(char)]
            
                # check characters to the left of current position
                hl_list = self.check_bracket_left(side, index, matching) + \
                        hl_list
        
        # junk characters: hl_list already contains just that char, so return
        
        return hl_list
        
    def delete_word(self, side, highlight_list):
        """ replace specified chars in text block with '.'s """
        
        if side == "left":
            text = self.left_text
        else:
            text = self.right_text
            
        for hl in highlight_list:
            
            index = self.screen_coords_to_string_index(
                    side, hl.screen_y, hl.screen_x)
            
            text = text[:index] + '.' + text[(index + 1):]
            
        if side == "left":
            self.left_text = text
        else:
            self.right_text = text
    
    '''    
    def get_selected_word(self, highlight_list):
        
        out = ""

        # sort by y, then x
        highlight_list.sort(key=lambda x: (x.text_y, x.text_x))
        
        for hl in highlight_list:
            
            out = out + hl.char
            
        return out
    '''
    def get_selected_word(self, hl_list):

        out = ""
        
        for ch in hl_list:
            
            out += ch.char
            
        return out

    def is_word(self, hl_list):
        
        return self.is_alpha(hl_list[0].char)
        
    def is_bracket_set(self, hl_list):
        
        return self.is_bracket(hl_list[0].char) and \
            len(hl_list) > 1
    
    '''        
    def text_coords_to_string_index(self, pos_y, pos_x):
        
        return pos_y * self.line_width + pos_x
        
    def string_index_to_text_coords(self, index):
        
        return (index / self.line_width), (index % self.line_width)
    '''
        
    def screen_coords_to_string_index(self, side, screen_y, screen_x):
        
        if side == "left":
            x_offset = self.left_lower
        else:
            x_offset = self.right_lower
        
        return (screen_y - self.row_start) * self.line_width + \
                (screen_x - x_offset)
        
    def string_index_to_screen_coords(self, side, index):
        
        if side == "left":
            x_offset = self.left_lower
        else:
            x_offset = self.right_lower
        
        return (index / self.line_width) + self.row_start, \
                (index % self.line_width) + x_offset
