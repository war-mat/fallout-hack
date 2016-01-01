#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

import lib.fallout_words as fallout_words
import lib.fallout_display as fallout_display
import lib.fallout_text as fallout_text
import lib.fallout_cursor as fallout_cursor

class Game(object):
    
    def __init__(self, screen):
        
        # use these to position elements (eventually)
        self.window_height, self.window_width = screen.getmaxyx()
        
        # word constants (should be based on difficulty)
        self.word_length = 7
        self.num_words = 15
        self.match_limit = 4
        
        # text/display constants
        self.line_width = 15
        self.num_rows = 17
        self.row_start = 6
        self.left_text_start = 8
        self.right_text_start = self.left_text_start + self.line_width + 8
        ROW_END = 22
        LEFT_ADDRESS_START = 1
        RIGHT_ADDRESS_START = LEFT_ADDRESS_START + 7 + self.line_width + 2
        self.right_cursor_pos = 49
            
        self.password = ""
        self.candidate_list = []
        
        # curses object for drawing
        self.screen = screen
        
        # display
        self.display = fallout_display.Display(
                self.screen, self.line_width, self.num_rows)
                
        # initialize game text object    
        self.game_text = fallout_text.GameText(
                self.row_start, self.left_text_start, 32, self.line_width, 
                self.num_rows)
        
        # initialize words object
        self.words = fallout_words.Words("/usr/share/dict/words")
        
        # initialize cursor object    
        self.cursor = fallout_cursor.Cursor(
                self.screen, 6, 8, 6, 1, self.line_width, self.num_rows)
        
        # remaining guesses
        self.attempts_left = 4
        
        # index = level, (word_length, num_words, match_limit)
        self.levels = [
            (4, 15, 3),
            (4, 15, 2),
            (5, 15, 3),
            (5, 15, 2)
            ]
        
        # make game text a dictionary
        self.messages = {"logo":"ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL",
            "command":"ENTER PASSWORD NOW",
            "attempts":"ATTEMPT(S) LEFT: ",
            "warning":"!!! WARNING: LOCKOUT IMMINENT !!!",
            "denied":"Entry denied.",
            "dud":"Dud removed."
            }
        
    def linear_distrib(self, num_of_numbers, upper_range):
    
        # number of choices and size of x axis
        x = upper_range + 1
        
        # y at x = 0 to form a triangle of area 1.0
        y = 2.0 / x
        
        # slope of the line from (0, y) to (x, 0) (rise over run)
        m = -y / x
        
        # offset size to place each x value at the middle of the line segments
        # created by dividing the x axis into 'x' number of discrete choices
        step = 1.0 / (x * 2)
        
        # using the formula for a line, find the y value (probability) for each
        # choice, given its position on the x axis
        probs = [((((i / float(x)) + step) * x) * m + y) \
            for i in xrange(0, upper_range + 1)]
        
        # probabilities should sum to 1.0, give or take floating point errors
        #print "sum of probs: %f" % sum(probs)
        
        num_list = [n for n in xrange(0, upper_range + 1)]
        out = []
        
        while len(out) < num_of_numbers:
            
            roll = random.uniform(0, 1)
            
            cumulative_prob = 0.0
            
            for num, num_prob in zip(num_list, probs):
                
                cumulative_prob += num_prob
                
                if roll < cumulative_prob:
                    
                    out.append(num)
                    break
            
        return out

    def remove_or_replenish(self):
        """
        Return results of a random choice. Odds are 1 in 4 'rep', 3 in 4 'dud'
        """
        
        result = ""
        
        roll = random.randint(0, 4)

        if roll == 0:
            result = "rep"
        else:
            result = "dud"
            
        return result
        
    def remove_random_candidate(self):
        """
        Remove a random word from password candidate list and return it.
        """
        
        # check if list is empty or not first
        
        index = random.randint(0, len(self.candidate_list) - 1)
        
        return self.candidate_list.pop(index)
        
    def set_game_word_params(self, level):
        
        self.word_length = self.levels[level][0]
        self.num_words = self.levels[level][1]
        self.match_limit = self.levels[level][2]

    def new_game(self, level):
        
        # clear all text on screen
        self.display.clear_all()
        
        # clear right text list
        self.game_text.reset_text_list()
        
        # set word params
        self.set_game_word_params(level)
        
        # reset attempts
        self.attempts_left = 4
        
        # generate distribution of random number of character matches
        self.match_distribution = self.linear_distrib(
                self.num_words, self.match_limit)
        
        self.game_text.left_text, self.game_text.right_text, self.password, self.candidate_list = \
                self.words.new_game(
                        self.word_length, self.num_words, 
                        self.match_distribution, self.line_width, self.num_rows)
                       
        # this needs to be it's own method
        self.game_text.left_text_block = self.game_text.string_to_2d_array(self.game_text.left_text)
        self.game_text.right_text_block = self.game_text.string_to_2d_array(self.game_text.right_text)
    
    def update_upper_text(self):
        
        # clear command/warning line
        self.display.print_str_delay(" " * 30, 2, 1, 0, 0)
        
        # update current command/warning line
        if self.attempts_left > 1:
            self.display.print_str_delay(self.messages["command"], 2, 1, 0, 0)
        else:
            self.display.print_str_delay(self.messages["warning"], 2, 1, 0, 0)
            
        # clear attempts indicators
        self.display.print_str_delay(" " * 7, 4, 18, 0, 0)
        
        # print remaining attempts
        self.display.print_attempts_left(self.attempts_left, 4, 18)
        
    def wrong_word(self, selected_word):
    
        # report letter correct / word_length
        correct = self.words.hamming_closeness(selected_word, self.password)
                        
        self.game_text.add_right_line(selected_word)
        self.game_text.add_right_line(self.messages["denied"])
                        
                        
        msg = "%d/%d correct." % (correct, self.word_length)
        self.game_text.add_right_line(msg)
                        
        self.display.erase_right_text()
        self.display.print_right_text_list(self.game_text.right_text_list)
                        
        # decrement attempts
        self.attempts_left -= 1
        
    def delete_word(self, word):
        
        # check left string first
        index = self.game_text.left_text.find(word)
            
        if index > -1:
            
            # replace
            self.game_text.left_text = self.game_text.left_text[:index] + '.' * self.word_length + \
                    self.game_text.left_text[index + self.word_length:]
                    
        else:
            
            index = self.game_text.right_text.find(word)
            
            self.game_text.right_text = self.game_text.right_text[:index] + '.' * self.word_length + \
                    self.game_text.right_text[index + self.word_length:]
                    
        # reconstruct 2d arrays
        self.game_text.left_text_block = self.game_text.string_to_2d_array(self.game_text.left_text)
        self.game_text.right_text_block = self.game_text.string_to_2d_array(self.game_text.right_text)
        
        # redraw
        
                
    def take_turn(self):
        
        self.update_upper_text()
        
        result = ""
        
        # check attempts remaing, fail if 0
        if self.attempts_left < 1:
            result = "lose"
        else:

            highlighted = self.game_text.get_highlighted(
                    self.cursor.side, self.cursor.cursor_y, 
                    self.cursor.cursor_x)
                
        
            # get character or word under cursor
            selected_word = self.game_text.get_selected_word(highlighted)
            
            # highlight character or word under cursor
            self.display.highlight(highlighted, 1)
            
            # print selected word at right cursor position
            self.display.print_right(selected_word, 0, 0)
            
            char = self.screen.getch()
                
            if char == ord('q'):
                result = "quit"
                
            elif char == ord(' '):
                
                # check if selected is a word, bracket set, or neither
                
                # write handler functions for word and bracket set
                
                if self.game_text.is_word(highlighted):
                        
                    # check if password or not
                    if selected_word == self.password:

                
                        self.display.print_right("password", 0, 0)
                            
                        char = self.screen.getch()
                        
                        result = "win"
                    else:
                        
                        self.wrong_word(selected_word)
                        
                elif self.game_text.is_bracket_set(highlighted):
                    
                    # bracket set selected code, needs to be it's own method
                    # not being reflected in the text strings, that's why it doesnt
                    # have any effect
                    self.game_text.delete_word(
                            self.cursor.side, highlighted)
                            
                    self.screen.refresh()
                    
                    #     
                    result = self.remove_or_replenish()

                    if result == "dud":
                        
                        remove = self.remove_random_candidate()
                        
                        self.game_text.add_right_line(selected_word)
                        self.game_text.add_right_line(self.messages["dud"])
                                        
                        self.display.erase_right_text()
                        self.display.print_right_text_list(self.game_text.right_text_list)
                        
                        # update left and right text to reflect removed word
                        self.delete_word(remove)
                        
                        self.display.text_block_update(
                                6, self.game_text.left_text_block, 
                                self.game_text.right_text_block, 8, 32)
                        
            else:
                # handle input
                self.cursor.handle_arrow_keys(char)
                
            # revert highlight
            self.display.highlight(highlighted, 0)
                
        return result

    def play_game(self):
        
        #self.display.clear_all()
        
        # print logo text at top
        self.display.print_str_delay(self.messages["logo"], 1, 1, 0, 20)
        
        # print command/warning line
        self.display.print_str_delay(self.messages["command"], 2, 1, 0, 20)

        # print remaining attempts
        self.display.print_str_delay(self.messages["attempts"], 4, 1, 0, 15)
        self.display.print_attempts_left(self.attempts_left, 4, 18)

        
        # display main text block
        self.display.print_game_text(
                1, 6, self.game_text.left_text_block, 
                self.game_text.right_text_block, self.game_text.address_list)
                
        # main game loop
        while True:
            
            result = self.take_turn()
            
            if result == "quit":
                break
            elif result == "win":
                return "win"
            elif result == "lose":
                
                # print lockout text
                break


# random chance to remove dud or replenish attempts
                
# remove word algo:
# select word from candidate list at random, candidate list should
# be saved in game state along with password
# if selected is not password, start with left block upper left space
# and right search to find that word
# if not found, repeat in right block
# delete it


# 1/7 correct.
# Dud removed.
# Allowance
# replenished.
# Access granted.
            

# program flow:
# start curses
# create Game() object
# Game __init__ should create all other objects, text, display, cursor, etc
# loop thru levels
# for each level, do game.new_game()
# newgame should reset all game variables

