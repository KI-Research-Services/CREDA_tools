# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 22:26:36 2020

@author: fisherd
"""

import re


class Addr_Parser:
    def __init__(self, address, testing=False):
        self.addresses = []
        self.flags = []
        address.strip()
        address = re.sub('\\.', '', address)
        if '(' in address:
            address = re.sub('\\(.+\\)', '', address)
            self.flags.append(Addr_Parser.Token('Err_02', typ='flag'))
        address = address.lower()
        pieces = re.split('( and |&|#|,|;|//|/| |-)', address)
        pieces = [i.strip() for i in pieces if i]
        pieces = [Addr_Parser.Token(i) for i in pieces if i]
        pieces = [i for i in pieces if i.strng != " "]
        
        if testing:
            print("Before:", end="")
            print(pieces, end="\n\n")

        pieces = self.initial_checks(pieces)
        if testing:
            print("After initial checks  : ", end="")
            print(pieces, end="\n\n")

        pieces = self.remove_consecutive_delims(pieces)
        if testing:
            print("After consecutive dels: ", end="")
            print(pieces, end="\n\n")

        pieces = self.num_size(pieces)
        if testing:
            print("After num_size        : ", end="")
            print(pieces, end="\n\n")

        pieces = self.check_alnums(pieces)
        if testing:
            print("After check_alnums    : ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_range(pieces)
        if testing:
            print("After combine_range: ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_pound(pieces)
        if testing:
            print("After combine_pound   : ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_multnums(pieces)
        if testing:
            print("After combine_multnums: ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_chars(pieces)
        if testing:
            print("After combine_chars   : ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_addrs(pieces)
        if testing:
            print("After combine_addrs   : ", end="")
            print(pieces, end="\n\n")

        pieces = self.combine_addr_pchars(pieces)
        if testing:
            print("After combine_addr_pchars: ", end="")
            print(pieces, end="\n\n")

        pieces = self.remove_addrs(pieces)
        if testing:
            print("After remove_addrs      : ", end="")
            print(pieces, end="\n\n")
            
        pieces = self.remove_flags(pieces)
        if testing:
            print("After remove_flags      : ", end="")
            print(pieces, end="\n\n")

        for piece in pieces:
            if piece.typ != 'del':
                self.flags.append(Addr_Parser.Token('Err_06', typ='flag'))

    class Token:
        def __init__(self, strng, typ='other'):
            '''takes a string and returns a token with a type'''
            if typ == 'other':
                if strng == 'and':
                    self.typ = 'del'
                elif strng == '&':
                    self.typ = 'del'
                elif strng == ',':
                    self.typ = 'del'
                elif strng == '#':
                    self.typ = 'pound'
                elif strng in ['apt', 'apts', 'unit', 'units', 'apartment', 'apartments', 'apn']:
                    self.typ = 'pound'
                elif strng == ';':
                    self.typ = 'del'
                elif strng == '/':
                    self.typ = 'del'
                elif strng == ' ':
                    self.typ = 'del'
                elif strng == 'and':
                    self.typ = 'del'
                elif strng.isdigit():
                    self.typ = 'num'
                elif strng == '-':
                    self.typ = 'rdel'  # range delimeter
                elif strng == 'through':
                    self.typ = 'rdel'  # range delimeter
                elif strng.isalpha():
                    self.typ = 'char'
                elif strng.isalnum():
                    self.typ = 'alnum'
                else:
                    self.typ = 'invalid'
            else:
                self.typ = typ
            self.strng = strng

        def __repr__(self):
            return f"'{self.strng}':'{self.typ}'"

    Error_Codes = {'Err_01':'No Numeric Found',
    'Err_02':'Parenthesis in address',
    'Err_03':'Apartment token without valid token following',
    'Err_04':'Possible bad range order',
    'Err_05':'Badly formed address',
    'Err_06':'Extra token after parsing',
    'Inf_01':'Contains Range Delimiter',
    'Inf_02':'Long Number',
    'Inf_03':'Ambiguous Direction, Unit',
    'Inf_04':'Has numbers divided by slash'
    }

    @staticmethod
    def initial_checks(pieces):
        has_num = False
        possible_range = False
        hasNumSlash=False
        for idx, piece in enumerate(pieces):
            if piece.typ == 'num':
                has_num = True
            if piece.typ == 'rdel':
                possible_range = 'True'
            if piece.typ == 'slash':
                if (piece[idx-1].typ=='num') and (piece[idx-1].typ=='num'):
                    hasNumSlash=True

        if not has_num:
            pieces.append(Addr_Parser.Token('Err_01', typ='flag'))
        if possible_range:
            pieces.append(Addr_Parser.Token('Inf_01', typ='flag'))
        if hasNumSlash:
            pieces.append(Addr_Parser.Token('Inf_04', typ='flag'))

        return pieces

    @staticmethod
    def remove_consecutive_delims(pieces):
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['del', 'rdel']:
                if (pieces[1].typ in ['del', 'rdel']):
                    if pieces[0].strng == ' ':
                        del pieces[0]
                    elif pieces[1].strng == ' ':
                        del pieces[1]
                    else:
                        temp_pieces.append(pieces[0])
                        del pieces[0]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)
        return temp_pieces

    @staticmethod
    def num_size(pieces):
        for piece in pieces:
            if piece.typ == 'num':
                if len(piece.strng) > 5:
                    pieces.append(Addr_Parser.Token("Inf_02", typ='flag'))
        return pieces

    @staticmethod
    def check_alnums(pieces):
        '''takes alnums (combination of numbers and alphabetical) and converts
        them into either numerical (e.g. 12a or 14b, an apt address), a char
        (5th, 1st, etc.), or two pieces, one of each (12ne to 12 ne) '''
        temp_pieces = []
        for i, piece in enumerate(pieces, 1):
            if piece.typ == 'alnum':
                # If it is a combined address and direction
                if re.match("^\\d+(?:n|e|s|w)$", piece.strng):
                    temp_piece = Addr_Parser.Token(piece.strng[-1:], typ="char")
                    piece.strng = piece.strng[:-1]
                    piece.typ = 'num'
                    pieces.insert(i, temp_piece)
                    temp_pieces.append(Addr_Parser.Token("Inf_03", typ='flag'))
                # If it is a combined address and direction
                elif re.match("^\\d+(?:nw|ne|sw|se)$", piece.strng):
                    temp_piece = Addr_Parser.Token(piece.strng[-2:], typ="char")
                    piece.strng = piece.strng[:-2]
                    piece.typ = 'num'
                    pieces.insert(i, temp_piece)
                # If it is a single apt letter
                elif re.match("^\\d+\\w$", piece.strng):
                    piece.typ = 'num'
                # If this represents a placement like 5th or 1st
                elif re.match("^\\d+(?:st|th|nd|rd)$", piece.strng):
                    piece.typ = 'char'
        for piece in temp_pieces:
            pieces.append(piece)
        return pieces

    @staticmethod
    def combine_pound(pieces):
        temp_pieces = []
        error_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ == 'pound':
                if (pieces[1].typ in ['char', 'num', 'multnum', 'range', 'alnum', 'pound']):
                    space = " " if len(pieces[0].strng)>1 else ""
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng}{space}{pieces[1].strng}', typ='pchar')
                    del pieces[1]
                else:
                    error_pieces.append(Addr_Parser.Token('Err_03', typ='flag'))
                    del pieces[0]
            elif pieces[0].typ == 'pchar':
                if (pieces[1].typ in ['char', 'num', 'multnum', 'range', 'alnum']):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='pchar')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)
        for piece in error_pieces:
            temp_pieces.append(piece)
        return temp_pieces

    @staticmethod
    def combine_chars(pieces):
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[0].typ == 'char':
                if pieces[1].typ in ['char','num', 'alnum']:
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='char')
                    del pieces[1]
                elif(pieces[1].strng in ['&', 'and']) and (pieces[2].typ == 'char'):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng} {pieces[2].strng}', typ='char')
                    del pieces[2]
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        while len(pieces) > 1:
            if pieces[0].typ == 'char':
                if pieces[1].typ in ['char','num', 'alnum']:
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='char')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)
        return temp_pieces

    @staticmethod
    def combine_multnums(pieces):
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['num', 'multnum', 'range']:
                if pieces[1].typ in ['num', 'range']:
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='multnum')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)

        pieces = temp_pieces
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[0].typ in ['num', 'multnum', 'range']:
                if (pieces[1].typ == 'del') and (pieces[2].typ in ['num', 'range']):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[2].strng}', typ='multnum')
                    del pieces[2]
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)

        return temp_pieces

    @staticmethod
    def combine_range(pieces):
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[1].typ == 'rdel':
                if (pieces[0].typ in ['char','num','alnum']) and (pieces[2].typ in ['char','num','alnum']):
                    pieces[1] = Addr_Parser.Token(f'{pieces[0].strng}-{pieces[2].strng}', typ='range')
                    del pieces[2]
                    del pieces[0]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)

        # This section corrects for ranges where full lenth of second piece has
        # been suppressed, e.g. 5101-09 -> 5101-5109
        for piece in temp_pieces:
            if piece.typ == 'range':
                piece1, piece2 = piece.strng.split("-")
                if len(piece1) > (len(piece2)):
                    piece2 = piece1[:len(piece1)-len(piece2)] + piece2
                    piece.strng = piece1 + "-" + piece2
                if piece2 < piece1:
                    temp_pieces.append(Addr_Parser.Token('Err_04', typ='flag'))

        return temp_pieces

    @staticmethod
    def combine_addrs(pieces):
        error = False
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['num', 'multnum', 'range']:
                if pieces[1].typ == 'char':
                    if pieces[0].typ == 'multnum':
                        for num in pieces[0].strng.split():
                            temp_pieces.append(Addr_Parser.Token(f'{num} {pieces[1].strng}', typ='address'))
                    else:
                        temp_pieces.append(Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address'))
                    del pieces[1]
                    del pieces[0]
                else:
                    error = True
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)
        if error:
            temp_pieces.append(Addr_Parser.Token('Err_05', typ='flag'))
        return temp_pieces

    @staticmethod
    def combine_addr_pchars(pieces):
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[0].typ == 'address':
                if (pieces[1].typ == 'del') and (pieces[2].typ == 'pchar'):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[2].strng}', typ='address')
                    del pieces[2]
                    del pieces[1]
                elif (pieces[1].typ == 'pchar'):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        while len(pieces) > 1:
            if pieces[0].typ == 'address':
                if (pieces[1].typ == 'pchar'):
                    pieces[0] = Addr_Parser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        for piece in pieces:
            temp_pieces.append(piece)
        return temp_pieces

    def remove_addrs(self, pieces):
        temp_pieces = []
        for piece in pieces:
            if piece.typ == 'address':
                self.addresses.append(piece)
            else:
                temp_pieces.append(piece)
        return temp_pieces
    
    def remove_flags(self, pieces):
        temp_pieces = []
        for piece in pieces:
            if piece.typ == 'flag':
                self.flags.append(piece)
            else:
                temp_pieces.append(piece)
        return temp_pieces

    def get_addrs(self):
        return [x.strng for x in self.addresses]

    def get_flags(self):
        temp_flags = []
        for flag in self.flags:
            temp_flags.append(f'{flag.strng} : {self.Error_Codes[flag.strng]}')
        return temp_flags
