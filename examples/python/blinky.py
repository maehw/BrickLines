from brick_lines import *

p = BrickLines()
p.append(BrickInstructionRepeat())
p.append(BrickInstructionSetOutput("out0", 0x01, 0.5))
p.append(BrickInstructionSetOutput("out1", 0x02, 0.5))
p.append(BrickInstructionForever())
p.connect("COM4")
p.run()
