import random
from Card import Card

class Dealer:
    def getAllCards(self):
        res = []

        colors = ['blue', 'red', 'yellow', 'green']
        specials = ['skip', 'reverse', 'draw_2'] * 2
        wilds = ['wild', 'wild_draw_4'] * 4 + ['wild_shuffle'] + ['white_wild'] * 3
        nums = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        for n in nums: # 数字カードを取得
            for c in colors:
                card = Card(c, None, n) 
                res.append(card)

        
        for c in colors: # 記号カードを取得
            for s in specials:
                card = Card(c, s, None)
                res.append(card)

        for w in wilds: # ワイルドカードを取得 とりあえず黒ってことに
            card = Card('black', w, None)
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

            print('put :p' + str(i) + ': ' + self.printCard(card)) # log
            self.baCards.append(card) # 場に出す
            self.beforeCard = card # 一番上のカードを更新
            self.cards[i].remove(card) #プレイヤの手札から削除

            if card.get('special') is not None:
                card_special = str(card.get('special'))
                if (card_special == 'skip'):
                    if self.isReverse:
                        self.playingIndex -= 1
                    else:
                        self.playingIndex += 1
                elif (card_special == 'draw_2'):
                    if self.isReverse:
                        self.playingIndex -= 1
                    else:
                        self.playingIndex += 1
                    self.drawCard(self.playingIndex) # 2ドロー
                    self.drawCard(self.playingIndex)
                elif (card_special == 'reverse'):
                    self.isReverse = not self.isReverse
                elif (card_special == 'wild'):
                    #処理 一旦無視
                    self.beforeCard.setColor(['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'wild_draw_4'):
                    #処理
                    if self.isReverse:
                        self.playingIndex -= 1
                    else:
                        self.playingIndex += 1
                    self.drawCard(self.playingIndex) # 4ドロー 色指定は一旦無視
                    self.drawCard(self.playingIndex)
                    self.drawCard(self.playingIndex)
                    self.drawCard(self.playingIndex)
                    self.beforeCard.setColor(['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'wild_shuffle'):
                    #処理 一旦無視
                    self.beforeCard.setColor(['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'white_wild'):
                    #処理 一旦無視
                    self.beforeCard.setColor(['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                    print('color changed for ' + self.beforeCard.get('color'))
                                
            return True

        if canDraw:
            self.drawCard(i)
        return False

    def printCard(self, card):
        if card.get('number') is not None:
            return(card.get('color') + ':' + str(card.get('number'))) #log
        else:
            return(card.get('color') + ':' + str(card.get('special'))) #log
        

    def drawCard(self, i): # カードをドローされるときの処理
        i = i % 4 #スキップとかのを考慮する
        card = self.yamaCards.pop(0)
        self.cards[i].append(card)
        print('draw :p' + str(i) + ': ' + self.printCard(card)) # log
        
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
        self.playingOder = [0, 1, 2, 3]
        self.isReverse = False
        self.playingIndex = 0

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
            while True:
                i = self.playingIndex
                if self.isPlaying[i]:
                    if self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, True):
                        if len(self.cards[i]) == 0:
                            self.isPlaying[i] = False
                            self.order.append(str(i))
                            print('p' + str(i) + ' :あがり')
                            flag = False
                            break
                    else:
                        self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, False)

                if self.isReverse:
                    self.playingIndex += -1
                else:
                    self.playingIndex += 1
                    
                self.playingIndex = self.playingIndex % 4
                    

        print('ゲーム終了')
        print(self.order)
