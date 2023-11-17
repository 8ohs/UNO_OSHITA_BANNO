import random

class RandomPlayer: # ランダムプレイヤ
    def selectCard(self, cards, beforeCard): # ランダムに手を選んで返す
        self.getGouhousyu(cards, beforeCard)
        if len(self.gouhousyu) == 0:
            return None
        return self.gouhousyu[random.randrange(len(self.gouhousyu))]

    def getGouhousyu(self, cards, beforeCard):
        self.gouhousyu.clear()
        for c in cards:
            if c.get('color') == beforeCard.get('color') or c.get('number') == beforeCard.get('number'):
                self.gouhousyu.append(c)
            
    def __init__(self, firstCardNum):
        self.firstCardNum = firstCardNum # モンテカルロ開始するときの所持カード枚数
        self.gouhousyu = []
