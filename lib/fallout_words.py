#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

class Words(object):
    
    def __init__(self, words_file):
        
        self.junk_list = list("<>(){}[]$.':_!\"+-%\/|*@#`=^;?,")
        
        self.open_words_file(words_file)
        
        self.password = ""
        self.candidate_list = []
    
    def is_ascii(self, word):
    
        try:
            word.decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True
    
    def open_words_file(self, words_file):
        
        with open(words_file, "r") as words:
            
            self.all_words = [w.strip() for w in words.readlines() if \
                not w[0].isupper() and ('\'' not in w) and self.is_ascii(w)]

    def gen_word_list(self, word_length):
        
        # return a list of all words of the specified length
        return [w.upper() for w in self.all_words if len(w) == word_length]
            
    def new_password(self, word_list):
        
        return random.choice(word_list)
        
    def hamming_closeness(self, word1, word2):
        """
        Return number of same characters, same location in two strings.
        Basically the inverse of Hamming distance.
        """
    
        if len(word1) != len(word2):
            raise ValueError("Undefined for sequences of unequal length")
        else:
            return sum(char1 == char2 for char1, char2 in zip(word1, word2))
            
    def insert_password_rand_pos(self, candidate_list, password):
    
        pos = random.randint(0, len(candidate_list))
        
        inserted = list(candidate_list)
        
        inserted.insert(pos, password)
        
        return inserted

    def new_candidate_words(self, match_distribution, num_words, word_list, 
        password):

        candidate_list = []
        
        for i in xrange(num_words):
        
            match = match_distribution[i]
    
            while True:
            
                # list of all words with that number of matches
                match_list = [w for w in word_list if \
                    self.hamming_closeness(w, password) == match]
                
                # if no matches found, change match number and retry
                if not match_list:
                    if match == 0:
                        match += 1
                    else:
                        match -= 1
                else:
                    # select a word from match list at random
                    random_select = random.choice(match_list)

                    # check if selected word != pw and hasn't been selected yet
                    if random_select != password and \
                        random_select not in candidate_list:
                        
                        candidate_list.append(random_select)
                        break
                    else:
                        # failed to find another word with given number of matches
                        # decrement matches by 1 and try again
                        match -= 1
                
        # double check resulting list of candidates
        if len(candidate_list) != num_words:
            raise Exception("Candidate word list failed to generate!")
        
        return candidate_list

    def gen_junk_string(self, length):
    
        out = ""
    
        for _ in xrange(length):
        
            out = out + random.choice(self.junk_list)
        
        return out
        
    def space_open(self, string, insert_index, word_len):
        
        available = True
            
        # check for word collisions, add 1 space so words are not back to back
        for i in xrange((insert_index - 1), insert_index + word_len + 1):
                
            # check for out of bounds indices
            if i < 0:
                i = 0
            elif i == len(string):
                i -= 1
                
            if string[i] not in self.junk_list:
                    
                # collision
                available = False
                break
                
        return available
        
    def insert_words(self, string, word_list):
    
        word_len = len(word_list[0])
        
        # maximum index for insertion
        max_pos = len(string) - word_len
        
        # words left to insert
        remaining = len(word_list)
        
        list_index = 0
        
        while remaining > 0:
            
            insert_word = word_list[list_index]
            
            # pick selection index at random
            insert_index = random.randint(0, max_pos)
            
            if self.space_open(string, insert_index, word_len):
                
                # perform insert
                string = string[:insert_index] + insert_word + \
                    string[(insert_index + word_len):]
                    
                remaining -= 1
                list_index += 1
                
        return string

    def compose_strings(self, candidate_list, line_width, num_rows):
        
        # divide candidate words into two equal lists
        candidate_split = len(candidate_list) / 2
        
        left_column_words = candidate_list[:candidate_split]
        right_column_words = candidate_list[candidate_split:]

        # generate strings of junk characters
        left_junk = self.gen_junk_string(line_width * num_rows)
        right_junk = self.gen_junk_string(line_width * num_rows)

        # insert words into junk text strings
        left_text = self.insert_words(left_junk, left_column_words)
        right_text = self.insert_words(right_junk, right_column_words)
        
        return list(left_text), list(right_text)

    def new_game(self, word_length, num_words, match_distribution, line_width,
        num_rows):
        
        # generate word list for current word length
        word_list = self.gen_word_list(word_length)

        # select a password
        password = self.new_password(word_list)
        
        # get other password candidates
        candidate_list = self.new_candidate_words(match_distribution, num_words,
            word_list, password)
            
        # add password to candidate list
        inserted_cl = self.insert_password_rand_pos(candidate_list, password)
        
        # compose text column contents
        left_text, right_text = self.compose_strings(inserted_cl, 
            line_width, num_rows)
            
        # return text lists, password, and list of candidate words (minus pw)
        return left_text, right_text, password, candidate_list
