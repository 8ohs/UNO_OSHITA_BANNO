class Card:
    def get(self, key):
        return self.info[key]

    def __init__(self, color, special, number):
        self.info = {'color': color, 'special': special, 'number': number}

    def setColor(self,color):
        self.info['color'] = color
