class Node:
    number: int
    weight: int
    directs_to: list

    def __init__(self, number, weight):
        self.number = number
        self.weight = weight
        self.directs_to = []
