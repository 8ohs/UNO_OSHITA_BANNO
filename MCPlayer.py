import random

class Card:
    def get(self, key):
        return self.info[key]

    def __init__(self, color, special, number):
        self.info = {'color': color, 'special': special, 'number': number}

class Dealer:
    def getAllCards(self):
        res = []

        colors = ['blue', 'red', 'yellow', 'green']
        nums = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        for n in nums:
            for c in colors:
                card = Card(c, '', n) #一旦記号カードは無視
                res.append(card)

        return res

    def putCard(self, card, i, canDraw): # カードが出されたときの処理
        def printAllCards(): # log
            print('player' + str(i) + 'の手持ち=======================')
            for c in self.cards[i]:
                print(c.get('color') + str(c.get('number')))
            print('\n')
            print('selected: ' + card.get('color') + str(card.get('number')))
            print('\n')
            
        if card is not None:
            # printAllCards()
            print('p' + str(i) + ': ' + card.get('color') + str(card.get('number'))) #log
            self.baCards.append(card) # 場に出す
            self.beforeCard = card # 一番上のカードを更新
            self.cards[i].remove(card) #プレイヤの手札から削除
            return True

        if canDraw:
            print('p' + str(i) + ' : choose draw') #log
            self.drawCard(i)
        return False
        
            

    def drawCard(self, i): # カードをドローされるときの処理        
        card = self.yamaCards.pop(0)
        self.cards[i].append(card)
        print('draw: ' + 'p' + str(i) + ': '  + card.get('color') + str(card.get('number'))) #log
        
        if len(self.yamaCards) == 0:
            print('山がゼロになりました')
            random.shuffle(self.baCards)
            for i in range(len(self.baCards)):
                self.yamaCards.append(self.baCards.pop(0))

    def __init__(self, p1, p2, p3, p4): # コンストラクタ(4人のプレイヤで初期化)
        self.players = [p1, p2, p3, p4]
        self.yamaCards = self.getAllCards() # 山のカード
        random.shuffle(self.yamaCards) # シャッフル
        self.baCards = [] # 場にある積まれたカード
        self.beforeCard = self.yamaCards.pop(0) # 一番上のカードを設定
        self.baCards.append(self.beforeCard)
        self.cards = []
        self.cards = [[] for _ in range(4)] # 各プレイヤの手札
        self.isPlaying = [True, True, True, True] # プレイ中かどうか
        self.order = [] # 勝利順

        # カードを配布
        print('初期手札を配布します')
        for p in range(4):
            for i in range(self.players[p].firstCardNum):
                self.drawCard(p)

        print('はじめのカード: ' + self.beforeCard.get('color') + str(self.beforeCard.get('number')))
        
                
    def isFinish(self): # ゲームが終了しているか判定
        count = 0
        for b in self.isPlaying:
            if b:
                count += 1

        if count >= 2:
            return False
        return True
                

    def gameStart(self): # ゲーム開始
        flag = True
        while flag: 
            for i in range(4):
                if self.isPlaying[i]:
                    if self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, True):
                        if len(self.cards[i]) == 0:
                            self.isPlaying[i] = False
                            self.order.append(str(i))
                            print('p' + str(i) + ' :あがり')
                        if self.isFinish(): #3人以上が0枚になったらゲーム終了
                            flag = False
                            break
                    else:
                        self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, False)

        print('ゲーム終了')
        print(self.order)

    
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
        self.cards = [] # 手札
        self.gouhousyu = []

# main
p1 = RandomPlayer(7)
p2 = RandomPlayer(7)
p3 = RandomPlayer(7)
p4 = RandomPlayer(7)

dealer = Dealer(p1, p2, p3, p4)
dealer.gameStart()
