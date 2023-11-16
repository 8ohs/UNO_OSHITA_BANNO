import random

class Card:
    def get(self, key):
        return self.info[key]

    def __init__(self, color, special, number):
        self.info = {'color': color, 'special': special, 'number': number}

class Dealer:
    def getAllCards():
        res = []

        colors = ['blue', 'red', 'yellow', 'green']
        nums = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        for n in nums:
            for c in colors:
                card = Card(c, '', n) #一旦記号カードは無視
                res.append(card)

        return res

    yamaCards = getAllCards() # 山のカード
    random.shuffle(yamaCards) # シャッフル
    baCards = []

    def putCard(self, card): # カードが出されたときの処理
        # 出せるカードなら (あとで実装)

        # else
        self.baCards.append(card)

    def drawCard(self): # カードをドローされるときの処理
        return self.yamaCards.pop(0)

    def __init__(self, p1, p2, p3, p4): # コンストラクタ(4人のプレイヤで初期化)
        self.players[p1, p2, p3, p4]

    def gameStart(self): # ゲーム開始
        while True:
            for i in range(4):
            self.putCard(self.players[i].selectCard())
            if self.players[i].getCardNum() == 0:
                break

    
class RandomPlayer: # ランダムプレイヤ
    cards = [] # 手札

    def selectCard(): # ランダムに手を選んで返す
        gouhousyu = getGouhousyu()
        res = 

    def getGouhousyu():

    def __init__(self, firstCardNum):
        self.firstCardNum = firstCardNumcardNum # モンテカルロ開始するときの所持カード枚数

# main
p1 = RandomPlayer(7)
p2 = RandomPlayer(7)
p3 = RandomPlayer(7)
p4 = RandomPlayer(7)

dealer = Dealer(p1, p2, p3, p4)
