import argparse
from curses import putp
import os
import math
import random
import sys
from turtle import pu
import socketio
import time
import copy

from rich import print

"""
定数
"""
# Socket通信の全イベント名
class SocketConst:
    class EMIT:
        JOIN_ROOM = 'join-room' # 試合参加
        RECEIVER_CARD = 'receiver-card' # カードの配布
        FIRST_PLAYER = 'first-player' # 対戦開始
        COLOR_OF_WILD = 'color-of-wild' # 場札の色を変更する
        UPDATE_COLOR = 'update-color' # 場札の色が変更された
        SHUFFLE_WILD = 'shuffle-wild' # シャッフルしたカードの配布
        NEXT_PLAYER = 'next-player' # 自分の手番
        PLAY_CARD = 'play-card' # カードを出す
        DRAW_CARD = 'draw-card' # カードを山札から引く
        PLAY_DRAW_CARD = 'play-draw-card' # 山札から引いたカードを出す
        CHALLENGE = 'challenge' # チャレンジ
        PUBLIC_CARD = 'public-card' # 手札の公開
        POINTED_NOT_SAY_UNO = 'pointed-not-say-uno' # UNO宣言漏れの指摘
        SPECIAL_LOGIC = 'special-logic' # スペシャルロジック
        FINISH_TURN = 'finish-turn' # 対戦終了
        FINISH_GAME = 'finish-game' # 試合終了
        PENALTY = 'penalty' # ペナルティ


# UNOのカードの色
class Color:
    RED = 'red' # 赤
    YELLOW = 'yellow' # 黄
    GREEN = 'green' # 緑
    BLUE = 'blue' # 青
    BLACK = 'black' # 黒
    WHITE = 'white' # 白


# UNOの記号カード種類
class Special:
    SKIP = 'skip' # スキップ
    REVERSE = 'reverse' # リバース
    DRAW_2 = 'draw_2' # ドロー2
    WILD = 'wild' # ワイルド
    WILD_DRAW_4 = 'wild_draw_4' # ワイルドドロー4
    WILD_SHUFFLE = 'wild_shuffle' # シャッフルワイルド
    WHITE_WILD = 'white_wild' # 白いワイルド


# カードを引く理由
class DrawReason:
    DRAW_2 = 'draw_2' # 直前のプレイヤーがドロー2を出した場合
    WILD_DRAW_4 = 'wild_draw_4' # 直前のプレイヤーがワイルドドロー4を出した場合
    BIND_2 = 'bind_2' # 直前のプレイヤーが白いワイルド（バインド2）を出した場合
    SKIP_BIND_2 = 'skip_bind_2' # 直前のプレイヤーが白いワイルド（スキップバインド2）を出した場合
    NOTHING = 'nothing' # 理由なし


TEST_TOOL_HOST_PORT = '3000' # 開発ガイドラインツールのポート番号
ARR_COLOR = [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE] # 色変更の選択肢


"""
コマンドラインから受け取った変数等
"""
parser = argparse.ArgumentParser(description='A demo player written in Python')
parser.add_argument('host', action='store', type=str, help='Host to connect')
parser.add_argument('room_name', action='store', type=str, help='Name of the room to join')
parser.add_argument('player', action='store', type=str, help='Player name you join the game as')
parser.add_argument('event_name', action='store', nargs='?', default=None, type=str, help='Event name for test tool') # 追加


args = parser.parse_args(sys.argv[1:])
host = args.host # 接続先（ディーラープログラム or 開発ガイドラインツール）
room_name = args.room_name # ディーラー名
player = args.player # プレイヤー名
event_name = args.event_name # Socket通信イベント名
is_test_tool = TEST_TOOL_HOST_PORT in host # 接続先が開発ガイドラインツールであるかを判定
SPECIAL_LOGIC_TITLE = '◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯' # スペシャルロジック名
TIME_DELAY = 10 # 処理停止時間


once_connected = False
id = '' # 自分のID
id1 = '' #自分の次のID(順番がTrueの時)
id2 = '' #自分の次の次のID
id3 = '' #自分の次の次のID
uno_declared = {} # 他のプレイヤーのUNO宣言状況


"""
コマンドライン引数のチェック
"""
if not host:
    # 接続先のhostが指定されていない場合はプロセスを終了する
    print('Host missed')
    os._exit(0)
else:
    print('Host: {}'.format(host))

# ディーラー名とプレイヤー名の指定があることをチェックする
if not room_name or not player:
    print('Arguments invalid')

    if not is_test_tool:
        # 接続先がディーラープログラムの場合はプロセスを終了する
        os._exit(0)
else:
    print('Dealer: {}, Player: {}'.format(room_name, player))


# 開発ガイドラインツールSTEP1で送信するサンプルデータ
TEST_TOOL_EVENT_DATA = {
    SocketConst.EMIT.JOIN_ROOM: {
        'player': player,
        'room_name': room_name,
    },
    SocketConst.EMIT.COLOR_OF_WILD: {
        'color_of_wild': 'red',
    },
    SocketConst.EMIT.PLAY_CARD: {
        'card_play': { 'color': 'black', 'special': 'wild' },
        'yell_uno': False,
        'color_of_wild': 'blue',
    },
    SocketConst.EMIT.DRAW_CARD: {},
    SocketConst.EMIT.PLAY_DRAW_CARD: {
        'is_play_card': True,
        'yell_uno': True,
        'color_of_wild': 'blue',
    },
    SocketConst.EMIT.CHALLENGE: {
        'is_challenge': True,
    },
    SocketConst.EMIT.POINTED_NOT_SAY_UNO: {
        'target': 'Player 1',
    },
    SocketConst.EMIT.SPECIAL_LOGIC: {
        'title': SPECIAL_LOGIC_TITLE,
    },
}


# Socketクライアント
sio = socketio.Client()


"""
ここに自分で作成した関数を配置する
"""
draw_event = False
card_count = 83     #山札のカード
select_color = 'green' #色選択の色
card_play = 1       #場のカード
card_hist = []                                             #使用したカードを辞書型として格納する
uno_hist = [[0 for i in range(10)] for j in range(9)]        #kindsと同様な形で使用されたら+1する
bindFlag = [0,0,0]  
removeCard = [None,None,None]
maxColor = 'green'
other_cards1 = []  #スタートする時点で自分の次のプレイヤーの確定している手札(id1)
other_cards2 = []  #スタートする時点で自分の前のプレイヤーの確定している手札(id3)
challengeNum = 0
challengeSuccess = 0

    


class RandomPlayer: # ランダムプレイヤ
    def selectCard(self, cards, beforeCard): # ランダムに手を選んで返す
        self.getGouhousyu(cards, beforeCard)
        if len(self.gouhousyu) == 0:
            return None
        return self.gouhousyu[random.randrange(len(self.gouhousyu))]

    def getGouhousyu(self, cards, beforeCard):
        self.gouhousyu.clear()

        for card in cards:
            card_special = card.get('special')
            card_number = card.get('number')
            if str(card_special) == 'wild_draw_4':
            # ワイルドドロー4は場札に関係なく出せる
                self.gouhousyu.append(card)
            elif (
                    str(card_special) == 'wild' or
                    str(card_special) == 'wild_shuffle' or
                    str(card_special) == 'white_wild'
            ):
            # ワイルド・シャッフルワイルド・白いワイルドも場札に関係なく出せる
                self.gouhousyu.append(card)
            elif str(card.get('color')) == str(beforeCard.get('color')):
            # 場札と同じ色のカード
                self.gouhousyu.append(card)
            elif (
                    (card_special and str(card_special) == str(beforeCard.get('special'))) or
                    ((card_number is not None or (card_number is not None and int(card_number) == 0)) and
                     (beforeCard.get('number') and int(card_number) == int(beforeCard.get('number'))))
            ):
            # 場札と数字または記号 が同じカード
                self.gouhousyu.append(card)

    def __init__(self, firstCardNum, removeCard, mustHaveCards):
        self.firstCardNum = firstCardNum # モンテカルロ開始するときの所持カード枚数
        self.gouhousyu = []
        self.removeCard = removeCard
        self.mustHaveCards = mustHaveCards

class MyDealer:
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
            if c not in self.yamaCards:#応急処置
                continue
            self.yamaCards.remove(c)
            if isAppendBaCards:
                self.baCards.append(c)
            if len(self.yamaCards) == 0:
                beforeCardCopy = self.baCards.pop(-1)
                random.shuffle(self.baCards)
                for i in range(len(self.baCards)):
                    self.yamaCards.append(self.baCards.pop(0))
                self.baCards.append(beforeCardCopy)

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


    def draw4Cards(self):#4draw
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)
        self.drawCard(self.playingIndex)

    
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
            self.beforeCard = copy.deepcopy(card) # 一番上のカードを更新
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
            for c in self.players[p].mustHaveCards:#確定分をセット
                if c is None:
                    continue
                if c in self.yamaCards:
                    self.yamaCards.remove(c)
                    self.cards[p].append(c)
                else:
                    self.cards[p].append(c)
                
        for p in range(4):
            for i in range(self.players[p].firstCardNum - len(self.players[p].mustHaveCards)): #確定分以外をセット
                if self.players[p].removeCard is not None:
                    yamaLen = len(self.yamaCards)
                    flag = False
                    rmCard = self.players[p].removeCard
                    for counter in range(yamaLen):
                        card = self.yamaCards.pop(0)
                        num = card.get('number')
                        special = card.get('special')     
                        if (card.get('color') == 'black' or card.get('color') == 'white' or card.get('color') == rmCard.get('color') or
                            (special and str(special) == str(rmCard.get('special'))) or
                            (num is not None or (num is not None and int(num) == 0)) and
                             rmCard.get('number') and int (num) == int(rmCard.get('number'))):
                            self.yamaCards.append(card)
                            if counter == yamaLen - 1:
                                flag = True
                        else:
                            self.cards[p].append(card)
                            break
                    if flag:
                        self.drawCard(p)
                else:
                    self.drawCard(p)

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
        if len(self.cards[0]) == 0:
             return self.calcMyScore()
        
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
    


"""
出すカードを選出する

Args:
    cards (list): 自分の手札
    before_caard (*): 場札のカード
"""
def select_play_card(cards, before_caard, data_res):
    startTime = time.perf_counter()#開始時間

    global card_hist
    global maxColor

    global removeCard
    cards_valid = [] # ワイルド・シャッフルワイルド・白いワイルドを格納
    cards_wild = [] # ワイルドドロー4を格納
    cards_wild4 = [] # 同じ色 または 同じ数字・記号 のカードを格納
    


    # 場札と照らし合わせ出せるカードを抽出する
    for card in cards:
        card_special = card.get('special')
        card_number = card.get('number')
        if str(card_special) == Special.WILD_DRAW_4:
            # ワイルドドロー4は場札に関係なく出せる
            cards_wild4.append(card)
        elif (
            str(card_special) == Special.WILD or
            str(card_special) == Special.WILD_SHUFFLE or
            str(card_special) == Special.WHITE_WILD
        ):
            # ワイルド・シャッフルワイルド・白いワイルドも場札に関係なく出せる
            cards_wild.append(card)
        elif str(card.get('color')) == str(before_caard.get('color')):
            # 場札と同じ色のカード
            cards_valid.append(card)
        elif (
            (card_special and str(card_special) == str(before_caard.get('special'))) or
            ((card_number is not None or (card_number is not None and int(card_number) == 0)) and
             (before_caard.get('number') and int(card_number) == int(before_caard.get('number'))))
        ):
            # 場札と数字または記号が同じカード
            cards_valid.append(card)

    numCardList = data_res.get('number_card_of_player')

    flag1 = False
    flag2 = True
    playersCardNum = []

    while flag2:
        for playerId, num in numCardList.items():
            if flag1:
                playersCardNum.append(num)
                if len(playersCardNum) == 3:
                    flag2 = False
                    break
            if playerId == data_res.get('next_player'):
                flag1 = True
 
    gouhousyu = cards_valid + cards_wild + cards_wild4
    if (len(gouhousyu) == 1 and len(cards) == 1): #手札が1枚かつ、合法手が1舞の時にそれをすぐ出す
        return gouhousyu[0]

    colorNum = [0] * 4
    for c in gouhousyu:
        if c.get('color') == 'red':
            colorNum[0] += 1
        if c.get('color') == 'blue':
            colorNum[1] += 1
        if c.get('color') == 'green':
            colorNum[2] += 1
        if c.get('color') == 'yellow':
            colorNum[3] += 1
    
    maxIndex = colorNum.index(max(colorNum))
    maxColor = ['red', 'blue', 'green', 'yellow'][maxIndex]

    wFlag = True
    wdFlag = True
    wsFlag = True
    wwFlag = True
    
    uniqueGouhousyu = [] #重複を排除した合法手
    for c in gouhousyu:
        if c.get('special') == 'wild':
            if wFlag:
                uniqueGouhousyu.append(c)
            wFlag = False
            continue
        elif c.get('special') == 'wild_draw_4':
            if wdFlag:
                uniqueGouhousyu.append(c)
            wdFlag = False
            continue
        elif c.get('special') == 'wild_shuffle':
            if wsFlag:
                uniqueGouhousyu.append(c)
            wsFlag = False
            continue
        elif c.get('special') == 'white_wild':
            if wwFlag:
                uniqueGouhousyu.append(c)
            wwFlag = False
            continue
        elif c not in uniqueGouhousyu:
            uniqueGouhousyu.append(c)

    putPatterns = [] #色選択を考慮した出す手の全パターン
    for c in uniqueGouhousyu:
        if (c.get('special') == 'wild' or
            c.get('special') == 'wild_draw_4'):
            for selectColor in ['red', 'blue', 'green', 'yellow']:
                card = {'color' : c.get('color'), 'special' : c.get('special'), 'selectColor' : selectColor}
                putPatterns.append(card)
        else:
            putPatterns.append(c)

    if len(putPatterns) == 1:
        return putPatterns[0]
    if len(putPatterns) == 0:
        return None

    putPatterns.append(None)#戦略パス
           
    tryNum = [0] * len(putPatterns) #試行回数
    scoreSum = [0] * len(putPatterns) #総得点 (勝利数にしたほうがいいか相談)
    scoreMean = [0] * len(putPatterns) #得点の平均

    mustHaveCards = [[] for _ in range(3)]#確定分を格納する
    global other_cards1
    global other_cards2

    mustHaveCards[0] = other_cards1
    mustHaveCards[2] = other_cards2

    p1 = RandomPlayer(0, None, mustHaveCards[1]) #自分の分身
    p2 = RandomPlayer(playersCardNum[0], removeCard[0], mustHaveCards[0])
    p3 = RandomPlayer(playersCardNum[1], removeCard[1], mustHaveCards[1])
    p4 = RandomPlayer(playersCardNum[2], removeCard[2], mustHaveCards[2])

    counter = 0#プレイアウト数
    while True:
        randNum = random.randrange(len(putPatterns))#乱数生成
        selectCard = putPatterns[randNum] #選ばれたカード
        fixedCard = selectCard
        if fixedCard is not None:
            fixedCard = selectCard.copy()
            if (selectCard.get('special') == 'wild' or#整形
                selectCard.get('special') == 'wild_draw_4' or
                selectCard.get('special') == 'wild_shuffle'):
                fixedCard['color'] = 'black'
            elif selectCard.get('special') == 'white_wild':
                fixedCard['color'] = 'white'

        dealer = MyDealer(p1, p2, p3, p4)
        dealer.removeCardsFromYama(copy.deepcopy(card_hist), True) #山から出されたカードを抜く
        dealer.removeCardsFromYama(cards, False) #山から自分の手札のカードを抜く
        dealer.isReverse =  not data_res.get('turn_right')#リバース中かどうかをセット
        dealer.setMyCards(cards.copy())#自分の手札をセット
        dealer.beforeCard = before_caard#場の一番上のカードをセット
        if fixedCard is not None and fixedCard.get('special') == 'wild_draw_4' and len(uniqueGouhousyu) != 1:#最初のみチャレンジが成功する場合必ずされる
            dealer.draw4Cards()
        else:
            dealer.putCard(fixedCard, 0, True)#カードを出す処理。Noneの場合は一枚引く
        dealer.skipPlayer()#自分の次の人の番にする
        tryNum[randNum] += 1#試行回数を増やす
        scoreSum[randNum] += dealer.gameStart()#プレイアウト。返り値は自分のスコア
        counter += 1

        if time.perf_counter() - startTime > 4.0: #4.5秒超えたら終わり
            break

    print('playout count = ' + str(counter))#log

    for i in range(len(putPatterns)):
        scoreMean[i] = scoreSum[i] / tryNum[i]#平均スコアを計算

    maxIndex = scoreMean.index(max(scoreMean))
    ansCard = putPatterns[maxIndex]

    if ansCard is None:
        return None
    
    selectCard = {}
    selectCard['color'] = ansCard.get('color')
    if ansCard.get('special') is not None:
        selectCard['special'] = ansCard.get('special')
    else:
        selectCard['number'] = ansCard.get('number')
    
    if ansCard.get('selectColor') is not None:
        global select_color
        select_color = ansCard.get('selectColor')
        
    return selectCard


"""
乱数取得

Args:
    num (int):

Returns:
    int:
"""
def random_by_number(num):
    return math.floor(random.random() * num)


"""
変更する色を選出する

Returns:
    str:
"""
def select_change_color():
    # このプログラムでは変更する色をランダムで選択する。
    global select_color
    return select_color

"""
チャンレンジするかを決定する

Returns:
    bool:
"""
def is_challenge(data):
    global id,challengeNum
    beforePlayerID = data.get('before_player')
    NumCardPlayer = data.get('number_card_of_player')
    myCardNum = 0
    challengeNum += 1
    for k, v in NumCardPlayer.items():
        if id == k:
            myCardNum = v
    
    if myCardNum == 1:  #自分の手札がラスト1枚のとき
        return True 
    elif beforePlayerID == id1 and other_cards1 is None:    #まだ相手の手札が全てわからないとき
        return True
    elif beforePlayerID == id3 and other_cards2 is None:
        return True
    
    return False

"""
他のプレイヤーのUNO宣言漏れをチェックする

Args:
    number_card_of_player (Any):
"""
def determine_if_execute_pointed_not_say_uno(number_card_of_player):
    global id, uno_declared

    target = None
    # 手札の枚数が1枚だけのプレイヤーを抽出する
    # 2枚以上所持しているプレイヤーはUNO宣言の状態をリセットする
    for k, v in number_card_of_player.items():
        if k == id:
            # 自分のIDは処理しない
            break
        elif v == 1:
            # 1枚だけ所持しているプレイヤー
            target = k
            break
        elif k in uno_declared:
            # 2枚以上所持しているプレイヤーはUNO宣言の状態をリセットする
            del uno_declared[k]

    if target == None:
        # 1枚だけ所持しているプレイヤーがいない場合、処理を中断する
        return

    # 抽出したプレイヤーがUNO宣言を行っていない場合宣言漏れを指摘する
    if (target not in uno_declared.keys()):
        send_event(SocketConst.EMIT.POINTED_NOT_SAY_UNO, { 'target': target })
        time.sleep(TIME_DELAY / 1000)


"""
個別コールバックを指定しないときの代替関数
"""
def pass_func(err):
    return


"""
送信イベント共通処理

Args:
    event (str): Socket通信イベント名
    data (Any): 送信するデータ
    callback (func): 個別処理
"""
def send_event(event, data, callback = pass_func):
    print('Send {} event.'.format(event))
    print('req_data: ', data)

    def after_func(err, res):
        if err:
            print('{} event failed!'.format(event))
            print(err)
            return

        print('Send {} event.'.format(event))
        print('res_data: ', res)
        callback(res)

    sio.emit(event, data, callback=after_func)


"""
受信イベント共通処理

Args:
    event (str): Socket通信イベント名
    data (Any): 送信するデータ
    callback (func): 個別処理
"""
def receive_event(event, data, callback = pass_func):
    co = copy.deepcopy(data)
    data = co
    global card_count           #山札の数
    #global card 
    global card_play            #場のカード数
    global card_hist            #場に出されたカードy
    global id,id1,id2,id3
    global removeCard
    global draw_event
    global bindFlag
    global other_cards1
    global other_cards2
    global id
    global id1
    global id3
    

    
        

    print('Receive {} event."'.format(event))
    print('res_data: ', data)
#初期設定
    if event == "first-player":
        i = 0
        play_order = data.get('play_order')
        while play_order[i] != id:
            i += 1
        
        for x in range(3):

            i += 1
            i = i % 4  #4になったら0にするため
            if x == 0:
                id1 = play_order[i]
            elif x == 1:
                id2 = play_order[i]
            elif x == 2:
                id3 = play_order[i]
            
        print(id1 , id2, id3)
        a = data.get('first_card')
        b = a.copy()
        card_hist.append(copy.deepcopy(b))

#シャッフルワイルドイベント
    if event == "shuffle-wild":
        removeCard = [None,None,None]
        other_cards1 = [None]
        other_cards2 = [None]

#プレイヤーがカードを引いた
        """
       if not( card_hist[-1].get("special") is not None and (card_hist[-1].get("special") == Special.WILD_DRAW_4 or card_hist[-1].get("special") == Special.DRAW_2)): 
        """
    if event == "draw-card":
        card_count -= 1  
    #ドローしたときの場のカードを記録する       

    if event == "draw-card" and draw_event == False:
        c = copy.deepcopy(card_hist[-1])
        if data.get('player') == id1 and bindFlag[0] == 0:
            removeCard[0] = c
        elif data.get('player') == id2 and bindFlag[1] == 0:
            removeCard[1] = c
        elif data.get('player') == id3 and bindFlag[2] == 0:
            removeCard[2] = c
    print(removeCard)
        #ドローしたらドローイベントを終了する
    if draw_event == True and (event == "draw-card"  or event == "challenge"):
        draw_event = False


    if event == "draw-card"  or event == "challenge":
        for i in range(3):
            # ループ内の処理
            if bindFlag[i] > 0:
                bindFlag[i] -= 1
                print(bindFlag)


#カードが場に出された
    
        

    if event == "play-card" or event == "play-draw-card":
       #カード情報格納
       d = data.get('card_play') 
       card = d.copy()

       if card and card.get('special') == Special.WHITE_WILD:       #バインド数を数える
            if data.get('player') ==  id:
                bindFlag[1] = 2
            elif data.get('player') == id1:
                bindFlag[2] = 2
            elif data.get('player') == id3:
                bindFlag[0] = 2
            
            print(bindFlag)
            
        #ホワイトワイルドの色を変更（白色だと履歴に不向き）
       if (card and card.get('special') ==  Special.WHITE_WILD): 
            beforeCard = card_hist[-1] 
            card['color'] = beforeCard.get("color")
            print(card)
       
       card_hist.append(copy.deepcopy(card))
       #print(uno_hist)
       #print(card_hist)
       print(card_hist)
       card_play += 1       #   カードプレイ数
       if (card and card.get('special') == Special.WILD_DRAW_4):
                card_count -= 3
                
       if (card and card.get('special') == Special.DRAW_2):
                card_count -= 1

       print(card_count)
       """
       if(card_count <= 0):
            keep = card_count * -1
            card_count = card_play - 1
            card_count -= keep
            card_play = 1
            card_hist = []
            card_hist.append(card)
            print(card_hist)
        """

    if event == "play-card":
        """
        if data.get('player') == id1 and removeCard[0] and removeCard[0].get('color') == card.get('color'):
            removeCard[0] = None
        if data.get('player') == id2 and removeCard[1] and removeCard[1].get('color') == card.get('color'):
            removeCard[1] = None
        if data.get('player') == id3 and removeCard[2] and removeCard[2].get('color') == card.get('color'):
            removeCard[2] = None
            print(removeCard)
        """
        if other_cards1 and card in other_cards1 and data.get('player') == id1:
            other_cards1.remove(card)
            print("id1の手札")
            print(other_cards1)
        
        if other_cards2 and card in other_cards2 and data.get('player') == id3:
            other_cards2.remove(card)
            print("id3の手札")
            print(other_cards1)
        
       
        if (card.get("special") is not None and
           (card.get('special') == Special.DRAW_2 or card.get('special') == Special.WILD_DRAW_4)):
            draw_event = True

    print(draw_event)



    if event == "challenge":
        if data.get('is_challenge_success') == False:
            card_count -= 3
        else:
            card_count -= 1         #予想
    """
    if(card_count <= 0):
        keep = card_count * -1
        card_count = card_play - 1
        card_count -= keep
        card_play = 1
        last_key,last_value = list(card_hist.items())[-1]
        card_hist.clear()
        card_hist.append(last_value)
        print(card_hist)
    """
    if event == 'update-color':         #シャッフルカードだけ色が黒と送られるため色を格納しなおす
        card = card_hist[-1]
        if (card.get('color') ==  Color.BLACK): 
            removed_element = card_hist.pop()
            card['color'] = data.get('color')
            card_hist.append(card.copy())
            print("append")

    if event == 'public-card':
        receive_cards = data.get('cards')
        if data.get('card_of_player') == id1:
            other_cards1 = copy.deepcopy(receive_cards)
            print("id1の手札カード")
            print(other_cards1)
        elif data.get('card_of_player') == id3:
            other_cards2 = copy.deepcopy(receive_cards)
            print("id3の手札カード")
            print(other_cards2)

    callback(data)


"""
Socket通信の確立
"""
@sio.on('connect')
def on_connect():
    print('Client connect successfully!')

    if not once_connected:
        if is_test_tool:
            # テストツールに接続
            if not event_name:
                # イベント名の指定がない（開発ガイドラインSTEP2の受信のテストを行う時）
                print('Not found event name')
            elif not event_name in TEST_TOOL_EVENT_DATA:
                # イベント名の指定があり、テストデータが定義されていない場合はエラー
                print('Undefined test data. eventName: ', event_name)
            else:
                # イベント名の指定があり、テストデータが定義されている場合は送信する(開発ガイドラインSTEP1の送信のテストを行う時)
                send_event(event_name, TEST_TOOL_EVENT_DATA[event_name])
        else:
            # ディーラープログラムに接続
            data = {
                'room_name': room_name,
                'player': player,
            }

            def join_room_callback(*args):
                global once_connected, id
                print('Client join room successfully!')
                once_connected = True
                id = args[0].get('your_id')
                print('My id is {}'.format(id))

            send_event(SocketConst.EMIT.JOIN_ROOM, data, join_room_callback)


"""
Socket通信を切断
"""
@sio.on('disconnect')
def on_disconnect():
    print('Client disconnect.')
    os._exit(0)


"""
Socket通信受信
"""
# プレイヤーがゲームに参加
@sio.on(SocketConst.EMIT.JOIN_ROOM)
def on_join_room(data_res):
    receive_event(SocketConst.EMIT.JOIN_ROOM, data_res)


# カードが手札に追加された
@sio.on(SocketConst.EMIT.RECEIVER_CARD)
def on_reciever_card(data_res):
    receive_event(SocketConst.EMIT.RECEIVER_CARD, data_res)


# 対戦の開始
@sio.on(SocketConst.EMIT.FIRST_PLAYER)
def on_first_player(data_res):
    receive_event(SocketConst.EMIT.FIRST_PLAYER, data_res)


# 場札の色指定を要求
@sio.on(SocketConst.EMIT.COLOR_OF_WILD)
def on_color_of_wild(data_res):
    def color_of_wild_callback(data_res):
        color = select_change_color()
        data = {
            'color_of_wild': color,
        }

        # 色変更を実行する
        send_event(SocketConst.EMIT.COLOR_OF_WILD, data)

    receive_event(SocketConst.EMIT.COLOR_OF_WILD, data_res, color_of_wild_callback)


# 場札の色が変わった
@sio.on(SocketConst.EMIT.UPDATE_COLOR)
def on_update_color(data_res):
    receive_event(SocketConst.EMIT.UPDATE_COLOR, data_res)


# シャッフルワイルドにより手札状況が変更
@sio.on(SocketConst.EMIT.SHUFFLE_WILD)
def on_shuffle_wild(data_res):
    def shuffle_wild_calback(data_res):
        global uno_declared
        uno_declared = {}
        for k, v in data_res.get('number_card_of_player').items():
            if v == 1:
                # シャッフル後に1枚になったプレイヤーはUNO宣言を行ったこととする
                uno_declared[data_res.get('player')] = True
                break
            elif k in uno_declared:
                # シャッフル後に2枚以上のカードが配られたプレイヤーはUNO宣言の状態をリセットする
                if data_res.get('player') in uno_declared:
                    del uno_declared[k]

    receive_event(SocketConst.EMIT.SHUFFLE_WILD, data_res, shuffle_wild_calback)


# 自分の番
@sio.on(SocketConst.EMIT.NEXT_PLAYER)
def on_next_player(data_res):
    def next_player_calback(data_res):
        determine_if_execute_pointed_not_say_uno(data_res.get('number_card_of_player'))

        cards = data_res.get('card_of_player')

        if (data_res.get('draw_reason') == DrawReason.WILD_DRAW_4):
            # カードを引く理由がワイルドドロー4の時、チャレンジを行うことができる。
            if is_challenge(data_res):
                send_event(SocketConst.EMIT.CHALLENGE, { 'is_challenge': True} )
                return

        if str(data_res.get('must_call_draw_card')) == 'True':
            # カードを引かないと行けない時
            send_event(SocketConst.EMIT.DRAW_CARD, {})
            return

        #  スペシャルロジックを発動させる
        special_logic_num_random = random_by_number(10)
        if special_logic_num_random == 0:
            send_event(SocketConst.EMIT.SPECIAL_LOGIC, { 'title': SPECIAL_LOGIC_TITLE })

        play_card = select_play_card(cards, data_res.get('card_before'),data_res)

        if play_card:
            # 選出したカードがある時
            print('selected card: {} {}'.format(play_card.get('color'), play_card.get('number') or play_card.get('special')))
            data = {
                'card_play': play_card,
                'yell_uno': len(cards) == 2, # 残り手札数を考慮してUNOコールを宣言する
            }

            if play_card.get('special') == Special.WILD or play_card.get('special') == Special.WILD_DRAW_4:
                color = select_change_color()
                data['color_of_wild'] = color

            # カードを出すイベントを実行
            send_event(SocketConst.EMIT.PLAY_CARD, data)
        else:
            # 選出したカードが無かった時

            # draw-cardイベント受信時の個別処理
            def draw_card_callback(res):
                if not res.get('can_play_draw_card'):
                    # 引いたカードが場に出せないので処理を終了
                    return

                # 以後、引いたカードが場に出せるときの処理
                data = {
                    'is_play_card': True,
                    'yell_uno': len(cards + res.get('draw_card')) == 2, # 残り手札数を考慮してUNOコールを宣言する
                }

                play_card = res.get('draw_card')[0]
                if play_card.get('special') == Special.WILD or play_card.get('special') == Special.WILD_DRAW_4:
                    global maxColor
                    color = maxColor
                    data['color_of_wild'] = color

                # 引いたカードを出すイベントを実行
                send_event(SocketConst.EMIT.PLAY_DRAW_CARD, data)

            # カードを引くイベントを実行
            send_event(SocketConst.EMIT.DRAW_CARD, {}, draw_card_callback)

    receive_event(SocketConst.EMIT.NEXT_PLAYER, data_res, next_player_calback)


# カードが場に出た
@sio.on(SocketConst.EMIT.PLAY_CARD)
def on_play_card(data_res):
    def play_card_callback(data_res):
        global uno_declared
        # UNO宣言を行った場合は記録する
        if data_res.get('yell_uno'):
            uno_declared[data_res.get('player')] = data_res.get('yell_uno')

    receive_event(SocketConst.EMIT.PLAY_CARD, data_res, play_card_callback)


# 山札からカードを引いた
@sio.on(SocketConst.EMIT.DRAW_CARD)
def on_draw_card(data_res):
    def draw_card_callback(data_res):
        global uno_declared
        # カードが増えているのでUNO宣言の状態をリセットする
        if data_res.get('player') in uno_declared:
            del uno_declared[data_res.get('player')]

    receive_event(SocketConst.EMIT.DRAW_CARD, data_res, draw_card_callback)


# 山札から引いたカードが場に出た
@sio.on(SocketConst.EMIT.PLAY_DRAW_CARD)
def on_play_draw_card(data_res):
    def play_draw_card_callback(data_res):
        global uno_declared
        # UNO宣言を行った場合は記録する
        if data_res.get('yell_uno'):
            uno_declared[data_res.get('player')] = data_res.get('yell_uno')

    receive_event(SocketConst.EMIT.PLAY_DRAW_CARD, data_res, play_draw_card_callback)


# チャレンジの結果
@sio.on(SocketConst.EMIT.CHALLENGE)
def on_challenge(data_res):
    receive_event(SocketConst.EMIT.CHALLENGE, data_res)


# チャレンジによる手札の公開
@sio.on(SocketConst.EMIT.PUBLIC_CARD)
def on_public_card(data_res):
    receive_event(SocketConst.EMIT.PUBLIC_CARD, data_res)


# UNOコールを忘れていることを指摘
@sio.on(SocketConst.EMIT.POINTED_NOT_SAY_UNO)
def on_pointed_not_say_uno(data_res):
    receive_event(SocketConst.EMIT.POINTED_NOT_SAY_UNO, data_res)


# 対戦が終了
@sio.on(SocketConst.EMIT.FINISH_TURN)
def on_finish_turn(data_res):
    def finish_turn__callback(data_res):
        global uno_declared
        uno_declared = {}
    #試合が終わったら初期化
    global card_hist 
    global card_count
    global removeCard
    global bindFlag
    global other_cards1
    global other_cards2

    card_hist.clear()
    card_count = 0
    removeCard = [None,None,None]
    bindFlag = [0,0,0]
    other_cards1 = [None]
    other_cards2 = [None]
    receive_event(SocketConst.EMIT.FINISH_TURN, data_res, finish_turn__callback)
        

# 試合が終了
@sio.on(SocketConst.EMIT.FINISH_GAME)
def on_finish_game(data_res):
    receive_event(SocketConst.EMIT.FINISH_GAME, data_res)


# ペナルティ発生
@sio.on(SocketConst.EMIT.PENALTY)
def on_penalty(data_res):
    def penalty_callback(data_res):
        global uno_declared
        # カードが増えているのでUNO宣言の状態をリセットする
        if data_res.get('player') in uno_declared:
            del uno_declared[data_res.get('player')]

    receive_event(SocketConst.EMIT.PENALTY, data_res, penalty_callback)


def main():
    sio.connect(
        host,
        transports=['websocket'],
    )
    sio.wait()

if __name__ == '__main__':
    main()
