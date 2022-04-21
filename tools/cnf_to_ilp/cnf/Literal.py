class Literal:
    index: int
    sign: bool

    def __init__(self, index: int, sign: bool):
        self.index = index
        self.sign = sign
