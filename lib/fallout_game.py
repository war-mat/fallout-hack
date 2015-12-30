#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

import lib.fallout_words as fallout_words
import lib.fallout_display as fallout_display
import lib.fallout_text as fallout_text
import lib.fallout_cursor as fallout_cursor

class Game(object):
    
    def __init__(self, screen):
        
        self.attempts_left = 4
        
        # make game text a dictionary
        self.messages = {"logo":"ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL",
            "command":"ENTER PASSWORD NOW",
            "attempts":"ATTEMPT(S) LEFT: ",
            "warning":"!!! WARNING: LOCKOUT IMMINENT !!!",
            "denied":"Entry denied."
            }
            
        # curses object for drawing
        self.screen = screen
            
        self.password = ""
        self.candidate_list = []

        
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
        
        index = random.randint(0, len(self.candidate_list))
        
        return self.candidate_list.pop(index)

    def new_game(self, num_words, match_limit, word_length, line_width, 
        num_rows):
        
        # generate distribution of random number of character matches
        self.match_distribution = self.linear_distrib(num_words, match_limit)

        # open words file and get list of all words of a given length
        self.words = fallout_words.Words("/usr/share/dict/words")
        
        left_text, right_text, self.password, self.candidate_list = \
            self.words.new_game(word_length, num_words, self.match_distribution,
            line_width, num_rows)
        
        # initialize game text object    
        self.game_text = fallout_text.GameText(6, 8, 32, 15, 17, left_text, 
            right_text)
            
        self.display = fallout_display.Display(
                self.screen, line_width, num_rows)
        
        # initialize cursor object    
        self.cursor = fallout_cursor.Cursor(
                self.screen, 6, 8, 6, 1, line_width, num_rows)
    
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
            
            # clear right hand line
            self.display.right_clear(49)
            
            self.display.print_right(selected_word, 49, 0, 0)
            
            char = self.screen.getch()
                
            if char == ord('q'):
                result = "quit"
            elif char == ord(' '):                
                # check if selected is a word, bracket set, or neither
                if self.game_text.is_word(highlighted):
                        
                    # check if password or not
                    if selected_word == self.password:
                            
                        self.display.right_clear(49)
                
                        self.display.print_right("password", 49, 0, 0)
                            
                        char = self.screen.getch()
                    else:
                        
                        # report letter correct / word_length
                        correct = self.words.hamming_closeness(
                                selected_word, self.password)
                        
                        # decrement attempts
                        self.attempts_left -= 1
                        
                elif self.game_text.is_bracket_set(highlighted):
                    
                    self.game_text.delete_word(
                            self.cursor.side, highlighted)
                        
                    result = self.remove_or_replenish()


                
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
                break
            elif result == "lose":
                
                # print lockout text
                break
            
            
# crashes if bracket section is too many characters
# need to add an upper limit to how many characters can be returned
# or just display them like "%^@#{ ... [[)|&" so it doesnt crash
# by highlight function

# random chance to remove dud or replenish attempts
                
# remove word algo:
# select word from candidate list at random, candidate list should
# be saved in game state along with password
# if selected is not password, start with left block upper left space
# and right search to find that word
# if not found, repeat in right block
# delete it
                    
# if hl_type == "word":
#   check for win
#   if not win, get hamming closeness to password and report
#   decrement attempts


                
# 1/7 correct.
# Dud removed.
# Allowance
# replenished.
# Entry granted.
            
