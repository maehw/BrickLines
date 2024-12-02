from brick_lines import *

p = BrickLines()
p.append(BrickInstructionSetOutput("all_off", 0x00, 2))
p.append(BrickInstructionSetOutput("all_on", 0x3F, 9999))
p.connect("COM4")
p.run()
