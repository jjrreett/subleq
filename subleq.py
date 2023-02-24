

class Data8:
    def __init__(self, value):
        if type(value) is Data8:
            self.value = value.value
            return 
        self.value = value&255
    
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
    if (x&0x80)>>7 == 1:
        return True 
    return False 
    
class Computer:
    def __init__(self) -> None:
        self.bus = "floating"
        self.register_a = 0x00
        self.register_b = 0x00
        self.alu_output = 0x00
        self.leq0_flag = 1
        self.ro = 0
        self.wa = 0
        self.wb = 0
    
    def update_alu(self) -> None:
        self.alu_output = (self.register_b + ((~self.register_a)&0xFF) + 1)&0xFF
        self.leq0_flag = 1 if self.alu_output==0 else 1 if (self.alu_output&0x80)>>7 else 0
    
    def clock_rise(self):
        # all reads to bus happen on clock rise
        # check if more than 1 read onto bus has happening (error)
        # if non, bus is indeterminate
        match self.ro + 0:
            case 0: 
                self.bus = "floating"
            case 1:
                pass
            case _:
                raise ValueError("reading multiple components to bus is indetermainte")
        
        if self.ro == 1:
            self.bus = self.alu_output

    def clock_fall(self):
        if self.wa == 1:
            if self.bus == "floating":
                raise ValueError("writing floating value into reg is bad")
            self.register_a = self.bus 

        if self.wb == 1:
            if self.bus == "floating":
                raise ValueError("writing floating value into reg is bad")
            self.register_b = self.bus 
        # last step of clock fall
        self.update_alu()
        pass 


def data3(x):
    if x<0:
        return 8+x 
    return x

def main():
    comp = Computer()
    comp.register_b = 0x0F
    comp.register_a = 0x2
    comp.clock_rise()
    comp.clock_fall()

    print(f"{comp.register_b:#010b}")

    comp.ro = 1
    comp.wb = 1
    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.register_b:#010b}")

    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.register_b:#010b}")

    comp.clock_rise()
    comp.clock_fall()
    print(f"{comp.register_b:#010b}")





if __name__ == "__main__":
    main()