import pytest
from intcode import IntCode

class AftScaffoldingControl:

    def __init__(self):
        self.brain = IntCode.create_from_source('day17_input.txt')
        self.brain.run()

    def read_camera(self):
        output = self.brain.output
        line = ''
        while not output.empty():
            pixel = output.get()
            if pixel == 10:
                print(line)
                line = ''
            else:
                line += chr(pixel)



# -----------------------------------------------


if __name__ == '__main__':
    pytest.main([__file__])

    ascii = AftScaffoldingControl()
    ascii.read_camera()