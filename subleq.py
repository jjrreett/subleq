class Data8:
    def __init__(self, value):
        if type(value) is Data8:
            self.value = value.value
            return
        self.value = value & 255

    def __str__(self):
        return f"{self.value:>08b}"

    def twos(self):
        return Data8(~self.value + 1)

    def __add__(self, b):
        if type(b) is not Data8:
            b = Data8(b)
        return Data8(self.value + b.value)

    def __neg__(self):
        return self.twos()

    def __sub__(self, b):
        if type(b) is not Data8:
            b = Data8(b)
        return self + -b


def is_leq0(x: int) -> bool:
    if x == 0:
        return True
    if (x & 0x80) >> 7 == 1:
        return True
    return False


class Computer:
    def __init__(self) -> None:
        self.bus = "floating"

        self.reg_a = 0x00
        self.reg_b = 0x00
        self.reg_add = 0x00
        self.pc = 0x00

        self.alu_out = 0x00
        self.mem_out = 0x00

        self.ro = 0
        self.rm = 0

        self.wa = 0
        self.wb = 0
        self.wd = 0 # read bus to address register
        self.inc_pc = 0
        self.rac = 0  # read address register into program counter
        self.car = 0  # choose address register

        self.leq0 = 1

    def update_alu(self) -> None:
        self.alu_out = (self.reg_b + ((~self.reg_a) & 0xFF) + 1) & 0xFF
        self.leq0 = 1 if self.alu_out == 0 else 1 if (self.alu_out & 0x80) >> 7 else 0

    def update_mem(self) -> None:
        if not self.car:
            address_bus = self.pc
        if self.car:
            address_bus = self.reg_add
        self.mem_out = self.mem[address_bus]

    def clock_rise(self):
        # all reads to bus happen on clock rise
        # check if more than 1 read onto bus has happening (error)
        # if non, bus is indeterminate
        match (self.ro, self.rm):
            case (0, 0):
                self.bus = "floating"
            case (1, 0):
                self.bus = self.alu_out
            case (0, 1):
                self.bus = self.mem_out
            case _:
                raise ValueError("reading multiple components to bus is indetermainte")

    def clock_fall(self):
        match (self.bus, self.wa, self.wb, self.wd):
            case ("floating", *rest) if any(rest):
                raise ValueError(
                    "a write into a register was attempted while the bus was floating"
                )
            case (x, *_):
                if self.wa:
                    self.reg_a = x
                if self.wb:
                    self.reg_b = x
                if self.wd:
                    self.reg_add = x
        if self.rac and self.inc_pc:
            raise ValueError("reading the address register into the program counter while incrementing the program counter is indetermainate behaivior")
        
        if self.rac:
            self.pc = self.reg_add

        if self.inc_pc == 1:
            self.pc = 0xFF & (self.pc + 1)

        self.update_mem()

        self.update_alu()

    def read_file_into_mem(self, file_path):
        with open(file_path, "rb") as file:
            data = file.read()
        self.mem = [data[i] for i in range(len(data))]


def data3(x):
    if x < 0:
        return 8 + x
    return x


def main():
    comp = Computer()
    comp.read_file_into_mem("mem")

    comp.clock_rise()
    comp.clock_fall()

    print(f"{comp.reg_b:#010b}")

    comp.ro = 1
    comp.wb = 1
    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.reg_b:#010b}")

    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.reg_b:#010b}")

    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.reg_b:#010b}")


if __name__ == "__main__":
    main()
