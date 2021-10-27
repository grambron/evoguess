class Literal:
    name: str
    sign: bool

    def __init__(self, name: str, sign: bool):
        self.name = name
        self.sign = sign
