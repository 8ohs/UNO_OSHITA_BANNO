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
        fixedCards = [] #直したカードのリスト
        for c in cards:
            if (c.get('special') == 'wild' or
                c.get('special') == 'wild_draw_4' or
                c.get('special') == 'wild_shuffle'):
                c['color'] = 'black'
            elif c.get('special') == 'white_wild':
                c['color'] = 'white'

            fixedCards.append(c)
        
        for c in fixedCards:
            self.yamaCards.remove(c)
            if isAppendBaCards:
                self.baCards.append(c)
            if len(self.yamaCards) == 0:
                beforeCardCopy = self.baCards.pop(-1)
                random.shuffle(self.baCards)
                for i in range(len(self.baCards)):
                    self.yamaCards.append(self.baCards.pop(0))
                self.baCards.append(beforeCardCopy)


    def draw4Cards(self):#4draw
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)

    def setMyCards(self, cards):
        for c in cards:
            if (c.get('special') == 'wild' or
                c.get('special') == 'wild_draw_4' or
                c.get('special') == 'wild_shuffle'):
                c['color'] = 'black'
                self.cards[0].append(c)
            elif c.get('special') == 'white_wild':
                c['color'] = 'white'
                self.cards[0].append(c)
            else:
                self.cards[0].append(c)
    
    def putCard(self, card, i, canDraw): # カードが出されたときの処理
        if card is not None:
            if card.get('selectColor') is not None: #色選択の要素を削除
                selectColor = card.get('selectColor')
                card = {'color' : 'black', 'special' : card.get('special')} 
            else:
                selectColor = (['blue', 'red', 'yellow', 'green'][random.randrange(4)]) #色決め
                
            #print('put :p' + str(i) + ': ' + self.printCard(card)) # log
            self.baCards.append(card) # 場に出す
            beforeCaradColor = self.beforeCard.get('color')#シャッフルカードの処理のために１つ前の色を取得
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
                elif (card_special == 'wild_draw_4'): # 4ドロー 
                    self.skipPlayer()
                    self.draw4Cards()
                    self.beforeCard['color'] = selectColor
                elif (card_special == 'wild_shuffle'): #シャッフル
                    self.shuffleCards()
                    self.beforeCard['color'] = selectColor
                elif (card_special == 'white_wild'): #白いワイルド
                    self.beforeCard['color'] = beforeCaradColor
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
        
        if len(self.yamaCards) == 0:
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
        self.isReverse = False
        self.playingIndex = 0


    def setUp(self): # セットアップ
        for p in range(4):
            for i in range(self.players[p].firstCardNum):
                if self.players[p].removeCard is not None:
                    yamaLen = len(self.yamaCards)
                    flag = False
                    rmCard = self.players[p].removeCard
                    for counter in range(yamaLen):
                        card = self.yamaCards.pop(0)
                        num = card.get('number')
                        special = card.get('special')
                        
                        print('tmp card == {}'.format(card))
                        if (card.get('color') == 'black' or card.get('color') == 'white' or card.get('color') == rmCard.get('color') or
                            (special and str(special) == str(rmCard.get('special'))) or
                            (num is not None or (num is not None and int(num) == 0)) and
                             rmCard.get('number') and int (num) == int(rmCard.get('number'))):
                            self.yamaCards.append(card)
                            print('not put')
                            if counter == yamaLen - 1:
                                flag = True
                        else:
                            self.cards[p].append(card)
                            print('put and break')
                            break
                    if flag:
                        self.drawCard(p)
                        print('naikara tekitouni')
                else:
                    print('somosomo tekitou')
                    self.drawCard(p)

        for p in range(4):
            print('p' + str(p) + '=========')
            for c in self.cards[p]:
                print(c)
            print('p' + str(p) + '=========')
                        

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
                        break
                else:
                    self.putCard(self.players[i].selectCard(self.cards[i], self.beforeCard), i, False)
            else: #バインド中のプレイヤの処理
                self.bindTurn[i] -= 1
                self.putCard(None, i, True)

            if self.isReverse:
                self.playingIndex += -1
            else:
                self.playingIndex += 1
                    
            self.playingIndex = self.playingIndex % 4
                    
        return self.calcMyScore()
