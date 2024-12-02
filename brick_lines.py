# Brick LINES: simple programs for the Interface A
# Copyright (C) 2024 maehw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
from colorama import init as colorama_init, Fore, Back, Style
from time import sleep
from enum import Enum

colorama_init()

class BrickFileFormat(Enum):
    AUTO_DETECT = 1
    COMMODORE = 2
    APPLE_II = 3

class BrickInstruction:
    def __init__(self, label, in7_condition, in6_condition, out_bit_pattern, value):
        self.label = label
        self.in7_condition = in7_condition
        self.in6_condition = in6_condition
        self.out_bit_pattern = out_bit_pattern
        self.value = value

    def __repr__(self):
        # 0123456789AB │▒▒▒│▒▒▒│ 1 │ 0 │ 1 │ 0 │ 1 │ 0 │ 1234
        r = f"{self.label: <12} "

        if self.in7_condition is None:
            r += "│▒▒▒"
        elif self.in7_condition is True:
            r += "│ 1 "
        else:
            r += "│ 0 "

        if self.in6_condition is None:
            r += "│▒▒▒│"
        elif self.in6_condition is True:
            r += "│ 1 │"
        else:
            r += "│ 0 │"

        if self.out_bit_pattern is None:
            r += "                       │"
        else:
            for pos in range(5, -1, -1):
                if self.out_bit_pattern & (1 << pos):
                    r += " 1 │"
                else:
                    r += " 0 │"
        r += " "
        if self.value is None:
            r += "     "
        else:
            r += f"{self.value: <5}"
        return r

class BrickInstructionSetOutput(BrickInstruction):
    def __init__(self, label, out_bit_pattern, value=None):
        super().__init__(label, None, None, out_bit_pattern, value)

class BrickInstructionRepeat(BrickInstruction):
    def __init__(self, value=None):
        super().__init__("REPEAT", None, None, None, value)

class BrickInstructionRepeatEnd(BrickInstruction):
    def __init__(self, label, in7_condition, in6_condition):
        super().__init__(label, in7_condition, in6_condition, None, None)

class BrickInstructionUntil(BrickInstructionRepeatEnd):
    def __init__(self, in7_condition, in6_condition):
        assert (in7_condition is not None) or (in6_condition is not None), "No real condition present, cannot accept any value for both IN7 and IN6"
        super().__init__("UNTIL", in7_condition, in6_condition)

class BrickInstructionEndrepeat(BrickInstructionRepeatEnd):
    def __init__(self):
        super().__init__("ENDREPEAT", None, None)

class BrickInstructionForever(BrickInstructionRepeatEnd):
    def __init__(self):
        super().__init__("FOREVER", None, None)

class BrickInstructionIf(BrickInstruction):
    def __init__(self, in7_condition, in6_condition):
        super().__init__("IF", in7_condition, in6_condition, None, None)

class BrickInstructionEndif(BrickInstruction):
    def __init__(self):
        super().__init__("ENDIF", None, None, None, None)

class BrickInstructionCount(BrickInstruction):
    def __init__(self, in7_condition, in6_condition, count):
        assert (in7_condition is not None) or (in6_condition is not None), "No real condition present, cannot accept any value for both IN7 and IN6"
        super().__init__("COUNT", in7_condition, in6_condition, None, count)


class BrickLines:
    def __init__(self):
        self.instructions = []
        self.serial_connection = None

    def connect(self, serial_port):
        import serial

        if self.serial_connection is not None:
            self.serial_connection.close()

        self.serial_connection = serial.Serial(serial_port, 19200)  # TODO check timeout
        self.set_outputs(0)  # turn outputs off initially

    def from_file(self, filename, file_format=BrickFileFormat.AUTO_DETECT):
        assert isinstance(file_format, BrickFileFormat)
        assert file_format in [BrickFileFormat.AUTO_DETECT, BrickFileFormat.COMMODORE, BrickFileFormat.APPLE_II], "File format not supported"
        assert os.path.isfile(filename), "Invalid file path"
        self.instructions = []
        if file_format == BrickFileFormat.AUTO_DETECT:
            self.from_file_auto_detect(filename)
        elif file_format == BrickFileFormat.COMMODORE:
            self.from_file_commodore(filename)
        elif file_format == BrickFileFormat.APPLE_II:
            self.from_file_apple(filename)

    def from_file_auto_detect(self, filename):
        # DOS file format is currently unknown and hence not supported (yet?)
        is_commodore = False
        with open(filename, "rb") as file:
            content = file.read()
            if len(content) == 762 and \
                (content[0x280:0x2D1] == b'\x00' * 0x51) and \
                (content[0x2F9:] == b'\xff'):
                is_commodore = True
        if is_commodore:
            self.from_file_commodore(filename)
        else:
            self.from_file_apple(filename)

    def from_file_commodore(self, filename):
        num_llines_max = 40
        lline_length = 16
        lline_label_length_max = 12

        with open(filename, "rb") as file:
            content = file.read()
            assert len(content) == 762  # expecting a fixed length file independent of its LEGO Lines contents
            assert content[0x280:0x2D1] == b'\x00' * 0x51  # these bytes are always zero (unused reserved part of the file?)
            assert content[0x2F9:] == b'\xff'
            bit_patterns = content[0x2D1:-1]
            assert len(bit_patterns) == num_llines_max
            num_llines_free = bit_patterns.count(
                b'\xff')  # assuming that the b'\xff' bytes only come as block at the end, it's enough to simply count them!
            num_llines_used = num_llines_max - num_llines_free
            # debugging info
            #print(f"Number of llines used: {num_llines_used}")
            #print(f"Number of llines free: {num_llines_free}")
            assert content[
                   num_llines_used * lline_length: 0x280] == num_llines_free * lline_length * b'\x00'  # this area should also be unused
            for lline_no in range(num_llines_used):
                lline = content[lline_no * lline_length: (lline_no + 1) * lline_length]
                label = lline[:lline_label_length_max].rstrip(b'\x00').decode('ascii')
                value = lline[lline_label_length_max:].rstrip(b'\x00').decode('ascii')
                converted_value = self.convert_value(value)
                # print only for debugging
                #print(f"{label: <{lline_label_length_max}} {bit_patterns[lline_no]: <3} ", end="")
                #if converted_value:
                #    print(f"{converted_value: <4}")
                #else:
                #    print()
                if label in ['REPEAT', 'UNTIL', 'ENDREPEAT', 'FOREVER', 'IF', 'ENDIF', 'COUNT']:
                    # print("  Keyword detected!")
                    if label == 'REPEAT':
                        i = BrickInstructionRepeat(converted_value)
                    elif label == 'UNTIL':
                        in7_condition, in6_condition = self.convert_condition_commodore(bit_patterns[lline_no])
                        i = BrickInstructionUntil(in7_condition, in6_condition)
                    elif label == 'ENDREPEAT':
                        i = BrickInstructionEndrepeat()
                    elif label == 'FOREVER':
                        i = BrickInstructionForever()
                    elif label == 'IF':
                        in7_condition, in6_condition = self.convert_condition_commodore(bit_patterns[lline_no])
                        i = BrickInstructionIf(in7_condition, in6_condition)
                    elif label == 'ENDIF':
                        i = BrickInstructionEndif()
                    elif label == 'COUNT':
                        in7_condition, in6_condition = self.convert_condition_commodore(bit_patterns[lline_no])
                        i = BrickInstructionCount(in7_condition, in6_condition, converted_value)
                    else:
                        assert False, "Lazy programmer forgot something"

                else:
                    i = BrickInstructionSetOutput(label, bit_patterns[lline_no], converted_value)
                self.append(i)

    def from_file_apple(self, filename):
        with open(filename, "r") as file:
            flines = [fline.rstrip() for fline in file]

        num_flines = len(flines)
        # print(f"Num lines in file: {num_flines}")  # debugging only
        num_llines = int(flines[0])
        # print(f"Num lines in LEGO Lines: {num_llines}")  # debugging only

        assert num_flines == num_llines * 4 + 1, "Wrong number of encoded lines"

        for l in range(num_llines):
            fline_no = l * 4 + 1
            label_len = int(flines[fline_no])
            # print(flines[fline_no], end=", ")
            view = flines[fline_no + 1]
            label, view_pattern, number = self.split_view_apple(label_len, view)
            # pp = self.parse_view_pattern_apple(view_pattern)
            lline_type = int(flines[fline_no + 2])
            bit_pattern = int(flines[fline_no + 3])
            # debugging only
            #print(f"{label: <13}{pp} tp={lline_type}, bp={bit_pattern}", end="")
            #if number:
            #    print(f"   {number}")
            #else:
            #    print()
            self.append(self.convert2instruction_apple(label, lline_type, bit_pattern, number))

    def convert2instruction_apple(self, label, lline_type, b, value):
        if lline_type == 0:
            # user entered line
            assert b >= 0 and not b >= (2 << 7)
            i = BrickInstructionSetOutput(label, b, value)
        elif lline_type == 1:
            # condition/loop keyword with parameter in bit pattern
            assert label in ['IF', 'UNTIL', 'COUNT']
            in7_condition, in6_condition = self.convert_condition_apple(b)
            if label == 'UNTIL':
                i = BrickInstructionUntil(in7_condition, in6_condition)
            elif label == 'IF':
                in7_condition, in6_condition = self.convert_condition_apple(b)
                i = BrickInstructionIf(in7_condition, in6_condition)
            elif label == 'COUNT':
                in7_condition, in6_condition = self.convert_condition_apple(b)
                i = BrickInstructionCount(in7_condition, in6_condition, value)
            else:
                assert False, "Lazy programmer forgot something"

        elif lline_type == 2:
            # condition/loop keyword without parameter in bit pattern (may still be in value field!)
            assert label in ['REPEAT', 'ENDREPEAT', 'ENDIF', 'FOREVER']
            assert b == 0
            if label == 'REPEAT':
                i = BrickInstructionRepeat(value)
            elif label == 'ENDREPEAT':
                i = BrickInstructionEndrepeat()
            elif label == 'FOREVER':
                i = BrickInstructionForever()
            elif label == 'ENDIF':
                i = BrickInstructionEndif()
            else:
                assert False, "Lazy programmer forgot something"

        return i

    # only required for debugging
    @staticmethod
    def replace_symbols_apple(s):
        replaced = s.replace('JK', 'X').replace('LM', '0').replace('^_', '1').replace('HI', ' ').replace('II', ' ')
        return replaced

    # only required for debugging
    def parse_view_pattern_apple(self, pattern):
        left = pattern[:4]  # left from separator 'u'
        right = pattern[5:]  # right from 'u'
        left = self.replace_symbols_apple(left)
        right = self.replace_symbols_apple(right)
        replaced = f"{left} {right}"
        return replaced

    def append(self, instruction):
        assert isinstance(instruction, BrickInstruction)
        self.instructions.append(instruction)

    def __repr__(self):
        return self.show()

    @staticmethod
    def convert_value(value):
        converted_value = None
        if ('.' in value) or (',' in value):
            try:
                converted_value = float(value.replace(',', '.'))
            except ValueError:
                pass
        else:
            try:
                converted_value = int(value)
            except ValueError:
                pass
        return converted_value

    def split_view_apple(self, expected_label_len, view):
        assert view[0] == ';'
        assert view[11:14] == '~As'
        assert view[31:34] == 't~@'
        label = view[1:11].strip()
        assert len(label) == expected_label_len
        view_pattern = view[14:31]
        number = view[34:]
        convert_value = self.convert_value(number)
        return label, view_pattern, convert_value

    @staticmethod
    def convert_condition_commodore(bit_pattern):
        # could map known values only where 0x81 => in7=True, in6=None ("any"), and 0x42 => in7=None, in6=True;
        # but making some brave assumptions here: bits 7 and 8 hold the values where bits 1 and 0 tell to ignore or not

        # simple mapping:
        #in7_condition = None
        #in6_condition = None
        #if bit_pattern == 0x81:
        #    in7_condition = True
        #elif bit_pattern == 0x42:
        #    in6_condition = True

        if bit_pattern & (1 << 1):
            # ignore in7 ("any")
            in7_condition = None
        else:
            # if in7 not ignored, set True/False
            in7_condition = bool(bit_pattern & (1 << 7))

        if bit_pattern & (1 << 0):
            # ignore in6 ("any")
            in6_condition = None
        else:
            # if in6 not ignored, set True/False
            in6_condition = bool(bit_pattern & (1 << 6))

        return in7_condition, in6_condition

    @staticmethod
    def convert_condition_apple(bit_pattern):

        # actually this value (b) can be interpreted as a 4 bit number where...
        # - the two least significant bits contain the expected bits
        # - the two more significant bits contain a pattern of bits to be ignored ("any value")
        assert bit_pattern in [0,  # 0b00'00 = '00'
                     1,  # 0b00'01 = '01'
                     2,  # 0b00'10 = '10'
                     3,  # 0b00'11 = '11'
                     4,  # 0b01'00 = '0X'
                     # 5,  # 0b01'01 = '0X' (not used)
                     6,  # 0b01'10 = '1X'
                     # 7,  # 0b01'11 = '1X' (not used)
                     8,  # 0b10'00 = 'X0'
                     9,  # 0b10'01 = 'X1'
                     10,  # 0b10'10 = 'X0' (not used)
                     # 11, # 0b10'11 = 'X1' (not used)
                     # 12, # 0b11'00 = 'XX' (not allowed/ does not make sense)
                     # any other values from here on do not make sense either
                     ]

        if bit_pattern & (1 << 3):
            # ignore in7 ("any")
            in7_condition = None
        else:
            # if in7 not ignored, set True/False
            in7_condition = bool(bit_pattern & (1 << 1))

        if bit_pattern & (1 << 2):
            # ignore in6 ("any")
            in6_condition = None
        else:
            # if in6 not ignored, set True/False
            in6_condition = bool(bit_pattern & (1 << 0))

        return in7_condition, in6_condition

    @staticmethod
    def show_header():
        r =  "                      ┌ IN ───┬ OUT ──────────────────┐\n"
        r += "        BRICK Lines   ├───┬───┼───┬───┬───┬───┬───┬───┤\n"
        r += "                      │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 │\n"
        r += "┌─ # ──┬─ LABEL ──────┼───┼───┼───┼───┼───┼───┼───┼───┼───────┐\n"
        # some commented dummy lines to play with the layout
        #r += "│ > 99 │ 0123456789AB │▒▒▒│▒▒▒│ 1 │ 0 │ 1 │ 0 │ 1 │ 0 │ 1234  │\n"
        #r += "├──────┼──────────────┼───┼───┼───┼───┼───┼───┼───┼───┼───────┤\n"
        #r += "└──────┴──────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───────┘\n"
        return r

    @staticmethod
    def show_footer():
        r = "└──────┴──────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───────┘\n"
        return r

    def show_line(self, line_no, is_active=False):
        i = self.instructions[line_no]
        r = ""

        if is_active:
            r += Back.WHITE + Fore.BLACK

        r += "│ "

        if is_active:
            r += ">"
        else:
            r += " "

        r += f" {line_no+1: >2} │ " + i.__repr__() + " │\n"

        if is_active:
            r += Style.RESET_ALL

        return r

    def show(self, active_line_no=None):
        r = self.show_header()
        for line_no in range(0, len(self.instructions)):
            r += self.show_line(line_no, (active_line_no is not None) and (active_line_no == line_no))
        r += self.show_footer()
        return r

    def print(self, active_line_no=None, clear_screen=True):
        if clear_screen:
            self.clear_screen()
        r = self.show(active_line_no)
        print(r)

    # for debugging only; this method steps through all lines and marks them as active
    #def demo(self):
    #    for line_no in range(0, len(self.instructions)):
    #        self.print(active_line_no=line_no)
    #        if line_no < len(self.instructions)-1:
    #            sleep(2)

    def set_outputs(self, bit_pattern, wait_time=None):
        # print(f"  will set the outputs to {bit_pattern} & wait for {wait_time}")  # debugging only
        tx = bit_pattern.to_bytes(1, byteorder='little')  # don't care about byte order because it's a single byte anyway
        self.serial_connection.write(tx)
        # wait afterwards
        if wait_time is not None:
            sleep(wait_time)
        else:
            # FIXME: wait for default time; what is it? assume 1 second for now
            sleep(1)

    def read_inputs(self):
        rx = int.from_bytes(self.serial_connection.read())  # function call will block when serial connection timeout is not set
        in7 = bool(rx & (1 << 7))
        in6 = bool(rx & (1 << 6))
        return in7, in6

    def run(self):
        self.check()  # check syntax before execution!
        last_line_no = None  # 'last' not as 'in the end of the program' but 'from the last iteration'
        line_no = 0
        running = True
        loop_nesting = []
        end_line_no = len(self.instructions)
        if end_line_no == 0:
            # program is empty
            running = False
        while running:
            self.print(active_line_no=line_no)
            # print(f"Line no: {line_no}")
            i = self.instructions[line_no]
            if isinstance(i, BrickInstructionSetOutput):
                self.set_outputs(i.out_bit_pattern, i.value)
                last_line_no = line_no
                line_no += 1
            elif isinstance(i, BrickInstructionRepeat):
                # check whether loop is entered (from a line above) or
                # if still looping (another iteration)
                if (last_line_no is None) or (last_line_no < line_no):
                    # entering loop first
                    if i.value is not None:  # counted loop aka 'for loop'
                        # add another loop nesting level and set loop counter to 0
                        loop_nesting.append({'head': line_no, 'counter': 0})
                    else:
                        # add another loop nesting level and mark loop counter as invalid (irrelevant)
                        loop_nesting.append({'head': line_no, 'counter': None})
                # else:
                #    print("still in loop, nothing to do as condition has been checked before!")
                last_line_no = line_no
                line_no += 1
            elif isinstance(i, BrickInstructionUntil):
                last_line_no = line_no
                if self.check_inputs(i.in7_condition, i.in6_condition):
                    # condition has been met, break out of loop and continue below
                    line_no += 1
                    # remove nesting level
                    loop_nesting.pop()
                else:
                    # jump back to top of loop; no need to increment a loop counter
                    line_no = loop_nesting[-1]['head']
            elif isinstance(i, BrickInstructionEndrepeat):
                # counted loop aka 'for loop': increment and check (outermost) loop counter
                loop_nesting[-1]['counter'] += 1
                # print(f"  incremented for loop counter to {loop_nesting[-1]['counter']}")
                last_line_no = line_no
                if loop_nesting[-1]['counter'] == self.instructions[loop_nesting[-1]['head']].value:
                    # done, break out of loop
                    line_no += 1
                    # remove nesting level
                    loop_nesting.pop()
                else:
                    # jump back to top of loop
                    line_no = loop_nesting[-1]['head']
            elif isinstance(i, BrickInstructionForever):
                last_line_no = line_no
                # jump back to top of loop
                line_no = loop_nesting[-1]['head']
            elif isinstance(i, BrickInstructionIf):
                last_line_no = line_no
                if self.check_inputs(i.in7_condition, i.in6_condition):
                    line_no += 1
                else:
                    # go to end of if condition, look for the next ENDIF
                    for endif_candidate_line_no in range(line_no+1, end_line_no):
                        if isinstance(self.instructions[endif_candidate_line_no], BrickInstructionEndif):
                            line_no = endif_candidate_line_no  # or shall we go to +1 directly?
                            break  # do not keep searching for other candidates
            elif isinstance(i, BrickInstructionEndif):
                # nothing to do
                last_line_no = line_no
                line_no += 1
            elif isinstance(i, BrickInstructionCount):
                last_line_no = line_no
                in7, in6 = self.read_inputs()
                change_counter = 0
                while change_counter < i.value:
                    waiting_for_change = True
                    while waiting_for_change:
                        new_in7, new_in6 = self.read_inputs()
                        if (i.in7_condition is True) and (i.in6_condition is None):
                            if new_in7 != in7:
                                waiting_for_change = False
                        elif (i.in6_condition is True) and (i.in7_condition is None):
                            if new_in6 != in6:
                                waiting_for_change = False
                        else:
                            assert False, "Currently not supported; make sure this is really supported"
                        in7, in6 = new_in7, new_in6
                    change_counter += 1
                line_no += 1
            else:
                assert False, "Unknown instruction"
            if line_no >= end_line_no:
                running = False
                print(f"Hit program end: {line_no} >= {end_line_no}")
                self.print()

    @staticmethod
    def clear_screen():
        print("\033c\033[3J", end='')

    def check(self):
        nesting_levels_max = 8
        nesting = []
        line_no = 1
        for i in self.instructions:
            assert isinstance(i, BrickInstruction)

            if isinstance(i, BrickInstructionCount):
                assert i.value is not None, f"Line {line_no}: COUNT has no value"

            # closing an existing nesting level opened with a REPEAT or an IF
            if len(nesting) > 0:
                n = nesting[-1]
                ni = n['instruction']
                n_line_no = n['line_no']
                if isinstance(i, BrickInstructionUntil) or \
                        isinstance(i, BrickInstructionEndrepeat) or \
                        isinstance(i, BrickInstructionForever):
                    if isinstance(ni, BrickInstructionIf):
                        assert False, f"Line {n_line_no}: IF structure has no ending"
                    assert isinstance(ni,
                                      BrickInstructionRepeat), f"Line {n_line_no}: REPEAT structure has no beginning"
                    if isinstance(i, BrickInstructionEndrepeat):
                        assert ni.value is not None, f"Line {n_line_no}: ENDREPEAT has no matching REPEAT n statement"
                    nesting.pop()
                elif isinstance(i, BrickInstructionEndif):
                    if isinstance(ni, BrickInstructionRepeat):
                        assert False, f"Line {n_line_no}: REPEAT structure has no ending"
                    assert isinstance(ni, BrickInstructionIf), f"Line {n_line_no}: IF structure has no beginning"
                    nesting.pop()

            # opening a new nesting level with a REPEAT or an IF?
            if isinstance(i, BrickInstructionRepeat) or \
                    isinstance(i, BrickInstructionIf):
                assert len(nesting) < nesting_levels_max, f"Line {line_no}: Structures too deeply nested"
                nesting.append({'line_no': line_no, 'instruction': i})

            # assist debugging:
            # print(f"{line_no: >2}: {i}")
            # print(f"-- nesting: {nesting}")
            line_no += 1

        if len(nesting) > 0:  # not everything has been closed properly
            n = nesting[-1]
            ni = n['instruction']
            n_line_no = n['line_no']
            if isinstance(ni, BrickInstructionIf):
                assert False, f"Line {n_line_no}: IF structure has no ending"
            elif isinstance(ni, BrickInstructionRepeat):
                assert False, f"Line {n_line_no}: REPEAT structure has no ending"
            else:
                assert False

    def check_inputs(self, in7_condition, in6_condition):
        in7, in6 = self.read_inputs()
        if (in7_condition is not None) and (in6_condition is not None):
            # both inputs need to be checked
            condition = (in7 == in7_condition) and (in6 == in6_condition)
        elif in7_condition is not None:
            condition = (in7 == in7_condition)
        elif in6_condition is not None:
            condition = (in6 == in6_condition)
        else:
            assert False, "Software developer made a dumb logical error"
        return condition

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="BRICK Lines")
    parser.add_argument("-f", "--file", required=True, help="Input file name")
    parser.add_argument("-s", "--serial-port", help="Name of serial device to Interface A; required to run a program on")
    args = parser.parse_args()

    p = BrickLines()
    p.from_file(args.file)
    if args.serial_port is not None:
        p.connect(args.serial_port)
        p.run()
    else:
        p.print(clear_screen=False)
