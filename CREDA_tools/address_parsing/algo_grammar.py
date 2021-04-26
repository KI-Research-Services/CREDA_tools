# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 22:26:36 2020

@author: fisherd
"""

import re

class AddrParser:
    
    queens_zips = ['11354', '11355', '11356', '11357', '11358', '11359', '11360', '11365', '11366', '11367', '11412', '11423', '11432', '11433', '11434', '11435', '11436', '11101', '11102', '11103', '11104', '11105', '11106']

    def __init__(self, address: str, postal: str = None, city: str = None, testing: bool = False):
        '''
        Basic initialization function for the AddrParser object

        Parameters
        ----------
        address : str
            A single, string formatted address to be parsed
        postal : str
            The postal code of the property. Used to identify potential problem
            addresses like those in Queens, NY.
        city : str
            The city the property is in. Used to identify potential problem
            addresses like those in Queens, NY.
        testing : bool, optional
            A simple flag for whether the function is being run in test mode. If
            set to true, several print statements give output at each step. The
            default is False.

        Returns
        -------
        None.

        '''
        self.addresses = []
        self.flags = []
        self.city = city
        self.postal = postal
        address = address.strip()
        address = address.replace("'", "")
        address = re.sub('\\.', '', address)
        if address == '':
            self.flags.append(AddrParser.Token('AddrErr_00', typ='flag'))
            return
        if '(' in address:
            address = re.sub('\\(.+\\)', '', address)
            self.flags.append(AddrParser.Token('AddrErr_02', typ='flag'))
        address = address.lower()
        pieces = re.split('( and |&|#|,|;|//|/| |-)', address)
        pieces = [i.strip() for i in pieces if i]
        pieces = [AddrParser.Token(i) for i in pieces if i]
        pieces = [i for i in pieces if i.strng != " "]

        if testing:
            print("Before:", end="")
            print(pieces, end="\n\n")

        pieces = self.initial_checks(pieces)
        if testing:
            print("After initial checks  : ", end="")
            print(pieces, end="\n\n")
        
        pieces = self.non_address_checks(pieces)
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
                self.flags.append(AddrParser.Token('AddrErr_06', typ='flag'))

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

    Error_Codes = {'AddrErr_00':'No Address Record',
                   'AddrErr_02':'No Numeric Found',
                   'AddrErr_03':'Apartment token without valid token following',
                   'AddrErr_04':'Possible bad range order',
                   'AddrErr_05':'Badly formed address',
                   'AddrErr_06':'Extra token after parsing',
                   'AddrInf_01':'Contains Range Delimiter',
                   'AddrInf_02':'Long Number',
                   'AddrInf_03':'Ambiguous Direction, Unit',
                   'AddrInf_04':'Has numbers divided by slash',
                   'AddrInf_05':'Parenthesis in address',
                   'AddrInf_10':'Queens address'
                   }

    @staticmethod
    def initial_checks(pieces: list) -> list:
        '''
        This function performs initial checks on suitability of the address. Basic
        tests include presence of an alphanumeric, presence of range delimiter,
        and presence of a slash character.

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        pieces : list
            The token list making up the current address to be processed, now with
            information and error flags in case an initial check was activated.

        '''
        has_num = False
        possible_range = False
        has_num_slash = False
        for idx, piece in enumerate(pieces):
            if piece.typ == 'num':
                has_num = True
            if piece.typ == 'rdel':
                possible_range = 'True'
            if piece.typ == 'slash':
                if (piece[idx-1].typ == 'num') and (piece[idx-1].typ == 'num'):
                    has_num_slash = True

        if not has_num:
            pieces.append(AddrParser.Token('AddrErr_01', typ='flag'))
        if possible_range:
            pieces.append(AddrParser.Token('AddrInf_01', typ='flag'))
        if has_num_slash:
            pieces.append(AddrParser.Token('AddrInf_04', typ='flag'))

        return pieces
    
    def non_address_checks(self, pieces: list) -> list:
        '''
        This function does basic checks to see if there is a problem city/postal
        code at this address. For instance, it throws an information flag if it
        is a Queens address

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed, now with
            information and error flags in case an initial check was activated.

        Returns
        -------
        list
            DESCRIPTION.

        '''
        if self.postal in self.queens_zips:
            pieces.append(AddrParser.Token('AddrInf_10', typ='flag'))
        elif self.city == 'queens':
            pieces.append(AddrParser.Token('AddrInf_10', typ='flag'))
            
        return pieces
        

    @staticmethod
    def remove_consecutive_delims(pieces: list) ->list:
        '''
        This function removes problematic tokens that arise from inconsistent or
        extra spacing. This could be due to consecutive space characters, spaces
        around a range delimiter, etc.

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            modified to remove issues arising from extra spaces.

        '''
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['del', 'rdel']:
                if (pieces[1].typ in ['del', 'rdel']):
                    if pieces[0].strng == ' ':
                        del pieces[0]
                    elif pieces[1].strng == ' ':
                        del pieces[1]
                    if pieces[0].strng == ',':
                        del pieces[0]
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
    def num_size(pieces: list) -> list:
        '''
        A quick check for with numeric tokens contain numbers beyond length 5,
        as this is often indicative of an error in the address.

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list now processed for potentially long numerics.

        '''
        for piece in pieces:
            if piece.typ == 'num':
                if len(piece.strng) > 5:
                    pieces.append(AddrParser.Token("AddrInf_02", typ='flag'))
        return pieces

    @staticmethod
    def check_alnums(pieces: list) -> list:
        '''takes alnums (combination of numbers and alphabetical) and converts
        them into either numerical (e.g. 12a or 14b, an apt address), a char
        (5th, 1st, etc.), or two pieces, one of each (12ne to 12 ne) '''
        temp_pieces = []
        for i, piece in enumerate(pieces, 1):
            if piece.typ == 'alnum':
                # If it is a combined address and direction
                if re.match("^\\d+(?:n|e|s|w)$", piece.strng):
                    temp_piece = AddrParser.Token(piece.strng[-1:], typ="char")
                    piece.strng = piece.strng[:-1]
                    piece.typ = 'num'
                    pieces.insert(i, temp_piece)
                    temp_pieces.append(AddrParser.Token("AddrInf_03", typ='flag'))
                # If it is a combined address and direction
                elif re.match("^\\d+(?:nw|ne|sw|se)$", piece.strng):
                    temp_piece = AddrParser.Token(piece.strng[-2:], typ="char")
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
    def combine_pound(pieces: list) -> list:
        '''
        This provides look-ahead for pound symbols. If the current token list
        reflects an address with a pound symbol, e.g. "13 wilbur st, # 16", this
        code combines the last characters to "#16"

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            modified to correctly handle pound symbols.

        '''
        temp_pieces = []
        error_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ == 'pound':
                if (pieces[1].typ in ['char', 'num', 'multnum', 'range', 'alnum', 'pound']):
                    space = " " if len(pieces[0].strng) > 1 else ""
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng}{space}{pieces[1].strng}', typ='pchar')
                    del pieces[1]
                else:
                    error_pieces.append(AddrParser.Token('AddrErr_03', typ='flag'))
                    del pieces[0]
            elif pieces[0].typ == 'pchar':
                if (pieces[1].typ in ['char', 'num', 'multnum', 'range', 'alnum']):
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='pchar')
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
    def combine_chars(pieces: list) -> list:
        '''
        This function combines consecutive character strings. For instance, the
        tokenizing process turns "George Washington Blvd." into three separate
        character tokens. This would convert back to a single token.

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            removing adjacent character tokens.

        '''
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[0].typ == 'char':
                if pieces[1].typ in ['char', 'num', 'alnum']:
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='char')
                    del pieces[1]
                elif(pieces[1].strng in ['&', 'and']) and (pieces[2].typ == 'char'):
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng} {pieces[2].strng}', typ='char')
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
                if pieces[1].typ in ['char', 'num', 'alnum']:
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='char')
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
    def combine_multnums(pieces: list) -> list:
        '''
        This function provides for correct handling of multiple adjacent number
        and ranges, allowing correct parsing of string such as 1 3 5 wilbur lane

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            with properly combined numerics.

        '''
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['num', 'multnum', 'range']:
                if pieces[1].typ in ['num', 'range']:
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='multnum')
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
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[2].strng}', typ='multnum')
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
    def combine_range(pieces: list) -> list:
        '''
        This function handles correct processing of ranges, including those with
        incomplete second numbers (e.g. 5430-35)

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            with correct handling of abbreviated addresses.

        '''
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[1].typ == 'rdel':
                if (pieces[0].typ in ['char', 'num', 'alnum']) and (pieces[2].typ in ['char', 'num', 'alnum']):
                    pieces[1] = AddrParser.Token(f'{pieces[0].strng}-{pieces[2].strng}', typ='range')
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
                    temp_pieces.append(AddrParser.Token('AddrErr_04', typ='flag'))

        return temp_pieces

    @staticmethod
    def combine_addrs(pieces: list) -> list:
        '''
        This is a late-step function which starts joining valid address combinations.

        Parameters
        ----------
        pieces : list
            The token list making up the current address to be processed.

        Returns
        -------
        list
            The token list making up the current address to be processed, now
            hopefully with only address tokens and informational tokens.

        '''
        error = False
        temp_pieces = []
        while len(pieces) > 1:
            if pieces[0].typ in ['num', 'multnum', 'range']:
                if pieces[1].typ == 'char':
                    if pieces[0].typ == 'multnum':
                        for num in pieces[0].strng.split():
                            temp_pieces.append(AddrParser.Token(f'{num} {pieces[1].strng}', typ='address'))
                    else:
                        temp_pieces.append(AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address'))
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
            temp_pieces.append(AddrParser.Token('AddrErr_05', typ='flag'))
        return temp_pieces

    @staticmethod
    def combine_addr_pchars(pieces:list) -> list:
        '''
        Appends pchars (pound symbols, apartment numbers, etc) onto the end of the
        address.

        Parameters
        ----------
        pieces : list
            The token list, now of mainly addresses and informational tokens, that
            may also contain pchars - a post character like those for apartments.

        Returns
        -------
        list
            A list of completed address tokens, possibly with added pchars and
            informational tokens.

        '''
        temp_pieces = []
        while len(pieces) > 2:
            if pieces[0].typ == 'address':
                if (pieces[1].typ == 'del') and (pieces[2].typ == 'pchar'):
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[2].strng}', typ='address')
                    del pieces[2]
                    del pieces[1]
                elif pieces[1].typ == 'pchar':
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address')
                    del pieces[1]
                else:
                    temp_pieces.append(pieces[0])
                    del pieces[0]
            else:
                temp_pieces.append(pieces[0])
                del pieces[0]
        while len(pieces) > 1:
            if pieces[0].typ == 'address':
                if pieces[1].typ == 'pchar':
                    pieces[0] = AddrParser.Token(f'{pieces[0].strng} {pieces[1].strng}', typ='address')
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

    def remove_addrs(self, pieces: list) -> list:
        '''
        A finishing step that removes completed address tokens and adds them to
        the parser address list.

        Parameters
        ----------
        pieces : list
            The token list that has completed parsing and going through the grammar
            to make address tokens, with accompanying informational or error tokens.

        Returns
        -------
        temp_pieces : list
            A list of tokens, if any are left for this address, once all address
            tokens have been removed. These last will almost certainly be info or
            error tokens.

        '''
        temp_pieces = []
        for piece in pieces:
            if piece.typ == 'address':
                self.addresses.append(piece)
            else:
                temp_pieces.append(piece)
        return temp_pieces

    def remove_flags(self, pieces: list) -> list:
        '''
        This function removes informational and error tags discovered through the
        parsing process, and saves them to the parser object for this address.

        Parameters
        ----------
        pieces : list
            Parsed tokens after address tokens have been removed.

        Returns
        -------
        list
            Parsed tokens after valid addresses, error and info tokens have been
            removed. Left over tokens are treated as errors at this point.

        '''
        temp_pieces = []
        for piece in pieces:
            if piece.typ == 'flag':
                self.flags.append(piece)
            else:
                temp_pieces.append(piece)
        return temp_pieces

    def get_addrs(self):
        ''' Basic getter function for the fully parsed addresses '''
        return [x.strng for x in self.addresses]

    def get_flags(self):
        ''' Basic getter function for the error and informational flags flipped
        during the parsing process
        '''
        temp_flags = []
        for flag in self.flags:
            temp_flags.append(f'{flag.strng} : {self.Error_Codes[flag.strng]}')
        return temp_flags

    def get_status(self):
        '''
        Basic functio to return whether it has error flags

        Returns
        -------
        A T/F value based on whether it has error flags

        '''
        for flag in self.flags:
            if 'Err' in flag.strng:
                return True
        return False