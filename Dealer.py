import random

class Dealer:
    def getAllCards(self):#全部ある時の山札生成
        res = []

        colors = ['blue', 'red', 'yellow', 'green']
        specials = ['skip', 'reverse', 'draw_2'] * 2
        wilds = ['wild', 'wild_draw_4'] * 4 + ['wild_shuffle']
        nums = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        for n in nums: # 数字カードを取得
            for c in colors:
                card = {'color' : c, 'number' : n}
                res.append(card)

        
        for c in colors: # 記号カードを取得
            for s in specials:
                card = {'color' : c, 'special' : s}
                res.append(card)

        for w in wilds: # ワイルドカードを取得
            card = {'color' : 'black', 'special' : w}
            res.append(card)

        card = {'color' : 'white', 'special' : 'white_wild'}
        res.append(card)
        res.append(card)
        res.append(card)

        return res

    def removeCardsFromYama(self, cards, isAppendBaCards):#すでに出たカードなどを山から抜く
        for c in cards:
            self.yamaCards.remove(c)
            if isAppendBaCards:
                self.baCards.append(c)

    def draw4Challenge(self):#チャレンジ成功のときのみ呼ばれる
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.skipPlayer()

    
    def putCard(self, card, i, canDraw): # カードが出されたときの処理
        def printAllCards(): # log
            print('p' + str(i) + 'の手持ち=======================')
            for c in self.cards[i]:
                print(self.printCard(c))
            print('p' + str(i) + 'の手持ち=======================')

        #printAllCards()
        if card is not None:
            if card.get('selectColor') is not None: #色選択の要素を削除
                selectColor = card.get('selectColor')
                card = {'color' : 'black', 'special' : card.get('special')} 
            else:
                selectColor = (['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                
            print('put :p' + str(i) + ': ' + self.printCard(card)) # log
            self.baCards.append(card) # 場に出す
            self.beforeCard = card.copy() # 一番上のカードを更新
            self.cards[i].remove(card) #プレイヤの手札から削除

            if card.get('special') is not None:#何かしらの記号カードのとき
                card_special = str(card.get('special'))
                if (card_special == 'skip'):
                    self.skipPlayer()
                elif (card_special == 'draw_2'):
                    self.skipPlayer()
                    self.drawCard(self.playingIndex) # 2ドロー
                    self.drawCard(self.playingIndex)
                elif (card_special == 'reverse'):
                    self.isReverse = not self.isReverse
                elif (card_special == 'wild'):
                    self.beforeCard['color'] = selectColor
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'wild_draw_4'): # 4ドロー 
                    self.skipPlayer()
                    self.drawCard(self.playingIndex) 
                    self.drawCard(self.playingIndex)
                    self.drawCard(self.playingIndex)
                    self.drawCard(self.playingIndex)
                    self.beforeCard['color'] = selectColor
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'wild_shuffle'): #シャッフル
                    self.shuffleCards()
                    print('player' + "'" + 's cards have been shuffled')
                    self.beforeCard['color'] = selectColor
                    print('color changed for ' + self.beforeCard.get('color'))
                elif (card_special == 'white_wild'): #白いワイルド
                    self.beforeCard['color'] = self.baCards[-2].get('color')
                    print('bind ' + 'p' + str((self.playingIndex + 2) % 4) + ' for 2 turns')
                    self.bindTurn[(self.playingIndex + 2) % 4] += 2
                    self.skipPlayer()                                                  
            return True #カードを出したらTureを返す

        if canDraw: #カードを引けるターンなら
            self.drawCard(i)
        return False

    def skipPlayer(self):
        if self.isReverse:
            self.playingIndex -= 1
        else:
            self.playingIndex += 1

    def printCard(self, card):
        if card.get('number') is not None:
            return(card.get('color') + ':' + str(card.get('number'))) #log
        else:
            return(card.get('color') + ':' + str(card.get('special'))) #log

    def shuffleCards(self): #シャッフル
        allPlayersCard = self.cards[0] + self.cards[1] + self.cards[2] + self.cards[3]
        self.cards[0].clear()
        self.cards[1].clear()
        self.cards[2].clear()
        self.cards[3].clear()

        addNum = 0
        if self.isReverse:
            addNum = -1
        else:
            addNum = 1

        i = (self.playingIndex + addNum ) % 4
        
        for c in allPlayersCard:
            self.cards[i].append(c)
            i += addNum
            i %= 4

    def drawCard(self, i): # カードをドローされるときの処理
        i = i % 4 #スキップとかのを考慮する
        card = self.yamaCards.pop(0)
        self.cards[i].append(card)
        print('draw :p' + str(i) + ': ' + self.printCard(card)) # log
        
        if len(self.yamaCards) == 0:
            print('山がゼロになりました')
            beforeCardCopy = self.baCards.pop(-1)
            random.shuffle(self.baCards)
            for i in range(len(self.baCards)):
                self.yamaCards.append(self.baCards.pop(0))
            self.baCards.append(beforeCardCopy)

    def __init__(self, p1, p2, p3, p4): # コンストラクタ(4人のプレイヤで初期化)
        self.players = [p1, p2, p3, p4]
        self.yamaCards = self.getAllCards() # 山のカード
        random.shuffle(self.yamaCards) # シャッフル
        self.baCards = [] # 場にある積まれたカード
        self.beforeCard = None #場の一番上のカード
        self.cards = [[] for _ in range(4)] # 各プレイヤの手札
        self.bindTurn = [0, 0, 0, 0] # 残りバインドターン
        self.order = [] # 勝利順
        self.isReverse = False
        self.playingIndex = 0


    def setUp(self): # セットアップ
        print('初期手札を配布します')
        for p in range(4):
            for i in range(self.players[p].firstCardNum):
                self.drawCard(p)

        print('はじめのカード: {} : {}'.format(self.beforeCard.get('color'), self.beforeCard.get('special') or self.beforeCard.get('number')))

    def calcMyScore(self):
        scores = [0] * 4
        for i in range(4):
            for c in self.cards[i]:
                if c.get('number') is not None:
                    scores[i] -= c.get('number')
                elif (c.get('special') == 'skip' or
                      c.get('special') == 'reverse' or
                      c.get('special') == 'draw_2'):
                    scores[i] -= 20
                elif (c.get('special') == 'wild_shuffle' or
                      c.get('special') == 'white_wild'):
                    scores[i] -= 40
                else:
                    scores[i] -= 50

        for i in range(4):
            if len(self.cards[i]) == 0:
                scores[i] = sum(scores) * -1

        return scores[0]
        
            
    def gameStart(self): # ゲーム開始
        self.setUp()
        while True:
            i = self.playingIndex
            if self.bindTurn[i] == 0:
                if self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, True):
                    if len(self.cards[i]) == 0:
                        self.order.append(str(i))
                        print('p' + str(i) + ' :あがり')
                        break
                else:
                    self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, False)
            else: #バインド中のプレイヤの処理
                print('p' + str(i) + ' is in a bind')
                self.bindTurn[i] -= 1
                self.putCard(None, i, True)

            if self.isReverse:
                self.playingIndex += -1
            else:
                self.playingIndex += 1
                    
            self.playingIndex = self.playingIndex % 4
                    

        print('ゲーム終了')
        print(self.order)
        return self.calcMyScore()
