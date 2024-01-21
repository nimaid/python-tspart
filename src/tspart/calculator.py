from .constants import OpCode, DEFAULTS


class Calculator:
    def __init__(self,
                 first,
                 second=None,
                 opcode=None
                 ):
        self.first = first

        if second is None:
            self.second = DEFAULTS["second"]
        else:
            self.second = second

        if opcode is None:
            self.opcode = DEFAULTS["opcode"]
        else:
            if opcode not in OpCode:
                raise ValueError("The operation code must is not valid!")
            if opcode == OpCode.DIV and self.second == 0:
                raise ValueError("Cannot divide by zero!")
            self.opcode = opcode

    def add(self):
        return self.first + self.second

    def sub(self):
        return self.first - self.second

    def mult(self):
        return self.first * self.second

    def div(self):
        return self.first / self.second

    def operate(self):
        if self.opcode == OpCode.ADD:
            eq_string = f"{self.first} + {self.second}"
            value = self.add()
        elif self.opcode == OpCode.SUB:
            eq_string = f"{self.first} - {self.second}"
            value = self.sub()
        elif self.opcode == OpCode.MULT:
            eq_string = f"{self.first} * {self.second}"
            value = self.mult()
        elif self.opcode == OpCode.DIV:
            eq_string = f"{self.first} / {self.second}"
            value = self.div()
        else:
            raise ValueError(f"Invalid opcode: \"{self.opcode}\"")

        result = {
            "value": value,
            "equation": eq_string
        }

        return result
