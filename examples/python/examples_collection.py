from brick_lines import *

# a collection of examples; replace 'False' by 'True' to try the specific example

p = BrickLines()

# resources booklet, R11, "TWO"
if False:
    p.append(BrickInstructionSetOutput("both", 1 << 4 | 1 << 0, 5))
# resources booklet, R11, "FOUR"
elif False:
    p.append(BrickInstructionSetOutput("oneway", 1 << 0, 10))
    p.append(BrickInstructionSetOutput("pause", 0))
    p.append(BrickInstructionSetOutput("otherway", 1 << 1, 10))
# resources booklet, R11, "MLB"
elif False:
    p.append(BrickInstructionSetOutput("light", 1 << 4))
    p.append(BrickInstructionRepeat())
    p.append(BrickInstructionUntil(None, True))
    p.append(BrickInstructionSetOutput("oneway", 1 << 0, 2))
    p.append(BrickInstructionSetOutput("otherway", 1 << 1, 2))
# resources booklet, R11, "SEVEN", REPEAT UNTIL example
elif False:
    p.append(BrickInstructionRepeat())
    p.append(BrickInstructionSetOutput("off", 0, None))
    p.append(BrickInstructionUntil(None, True))
    p.append(BrickInstructionSetOutput("motoron", 1, 2))
# resources booklet, R11, "SIX", REPEAT ENDREPEAT example
elif False:
    p.append(BrickInstructionRepeat(10))
    p.append(BrickInstructionSetOutput("lighton", 1 << 4, None))
    p.append(BrickInstructionSetOutput("lightoff", 0, None))
    p.append(BrickInstructionEndrepeat())
# resources booklet, R11, "FIVE", REPEAT FOREVER example
elif False:
    p.append(BrickInstructionRepeat())
    p.append(BrickInstructionSetOutput("lighton", 1 << 4, None))
    p.append(BrickInstructionSetOutput("lightoff", 0, None))
    p.append(BrickInstructionForever())
# resources booklet, R11, "NINE", REPEAT FOREVER example
elif False:
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionSetOutput("motoron", 1 << 0, 2))
    p.append(BrickInstructionEndif())
# resources booklet, R11, "COUNT", COUNT example
elif False:
    p.append(BrickInstructionCount(True, None, 10))
    p.append(BrickInstructionSetOutput("motor", 1 << 0, 2))
# test code check: exceed number of allowed nesting levels (8)
elif False:
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
    p.append(BrickInstructionIf(None, True))
# test code check: REPEAT structure without ending
elif False:
    p.append(BrickInstructionRepeat())
# test code check: resources booklet, R11, try COUNT without a value
elif False:
    p.append(BrickInstructionCount(True, None, None))
# resources booklet, R11, try IF without an ending
elif False:
    p.append(BrickInstructionRepeat())
    p.append(BrickInstructionRepeat())
    p.append(BrickInstructionUntil(None, True))
    p.append(BrickInstructionSetOutput("motoron", 1, 2))
    p.append(BrickInstructionSetOutput("motoroff", 0, 2))
    p.append(BrickInstructionIf(True, None))
    p.append(BrickInstructionSetOutput("lighton", 1 << 5, 7))
    p.append(BrickInstructionForever())

p.print(active_line_no=0)
p.check()
#p.run()
