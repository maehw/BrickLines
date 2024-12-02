from brick_lines import *

serial_port = "COM4"

p = BrickLines()
duration = 0.2
p.append(BrickInstructionSetOutput("off_all", 0x00, 3))
p.append(BrickInstructionSetOutput("out_all", 0x3F, 3))
p.append(BrickInstructionRepeat())
p.append(BrickInstructionSetOutput("out0", 0x01, duration))
p.append(BrickInstructionSetOutput("out1", 0x02, duration))
p.append(BrickInstructionSetOutput("out2", 0x04, duration))
p.append(BrickInstructionSetOutput("out3", 0x08, duration))
p.append(BrickInstructionSetOutput("out4", 0x10, duration))
p.append(BrickInstructionSetOutput("out5", 0x20, duration))
p.append(BrickInstructionSetOutput("out4", 0x10, duration))
p.append(BrickInstructionSetOutput("out3", 0x08, duration))
p.append(BrickInstructionSetOutput("out2", 0x04, duration))
p.append(BrickInstructionSetOutput("out1", 0x02, duration))
p.append(BrickInstructionForever())
p.print(clear_screen=False)
p.connect(serial_port)
p.run()
