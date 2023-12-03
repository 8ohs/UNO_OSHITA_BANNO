from RandomPlayer import RandomPlayer
#from Dealer import Dealer
from MyDealer import Dealer
import random
import time

def main():
    startTime = time.perf_counter()#開始時間
    
    before_card = {'color' : 'yellow', 'number' : 9} #場のカードchallengeされない方
    #before_card = {'color' : 'green', 'number' : 9} #場のカードchallengeされる方
    
    playersCardNum = [7, 7, 7] # リバースされてないときの順番で自分の次の人から
    releasedCards = [{'color' : 'green', 'number' : 2}, {'color' : 'green', 'number' : 3}, {'color' : 'green', 'number' : 4}, {'color' : 'green', 'number' : 0}, {'color' : 'red', 'number' : 0}, {'color' : 'green', 'number' : 1}] # すでに出されたカードリスト
    cards = [{'color' : 'green', 'number' : 1}, {'color' : 'red', 'number' : 1}, {'color' : 'red', 'number' : 8}, {'color' : 'blue', 'special' : 'wild_draw_4'}, {'color' : 'black', 'special' : 'wild_draw_4'}, {'color' : 'red', 'special' : 'skip'}, {'color' : 'red', 'special' : 'draw_2'}] # 自分の手札
    isReverse = False #リバース中かどうか (リバース中ならTrue)

    # ここで手札とbefore_cardから合法手を選ぶ処理をする
        
    gouhousyu = [{'color' : 'blue', 'special' : 'wild_draw_4'}, {'color' : 'black', 'special' : 'wild_draw_4'}] # 合法手 challengeされない方
    #gouhousyu = [{'color' : 'green', 'number' : 1}, {'color' : 'blue', 'special' : 'wild_draw_4'}] # 合法手 challengeされる方

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

    putPatterns.append(None) #戦略的パス
                 
    tryNum = [0] * len(putPatterns) #試行回数
    scoreSum = [0] * len(putPatterns) #総得点 (勝利数にしたほうがいいか相談)
    scoreMean = [0] * len(putPatterns) #得点の平均

    removeCardList = [None] * 3
    rmCard = {'color' : 'green', 'number' : '2'}
    rmCard2 = {'color' : 'green', 'special' : 'skip'}
    rmCard3 = {'color' : 'green', 'special' : 'wild_draw_4'}
    removeCardList[0] = rmCard
    removeCardList[1] = rmCard2
    removeCardList[2] = rmCard3
    print(removeCardList)
    
    p1 = RandomPlayer(0, None) #自分の分身
    p2 = RandomPlayer(playersCardNum[0], removeCardList[0])
    p3 = RandomPlayer(playersCardNum[1], removeCardList[1])
    p4 = RandomPlayer(playersCardNum[2], removeCardList[2])

    #playOutNum = 6000 #プレイアウト数
    counter = 0

    #for i in range(playOutNum):
    while True:
        counter += 1
        randNum = random.randrange(len(putPatterns))#乱数生成
        selectedCard = putPatterns[randNum] #選ばれたカード
        dealer = Dealer(p1, p2, p3, p4)
        dealer.removeCardsFromYama(releasedCards, True) #山から出されたカードを抜く
        dealer.removeCardsFromYama(cards, False) #山から自分の手札のカードを抜く
        dealer.isReverse = isReverse #リバース中かどうかをセット
        dealer.setMyCards(cards.copy())#自分の手札をセット
        dealer.beforeCard = before_card#場の一番上のカードをセット
        if selectedCard is not None and selectedCard.get('special') == 'wild_draw_4' and len(gouhousyu) != 1:#最初のみチャレンジが成功する場合必ずされる
            dealer.draw4Cards()
        else:
            dealer.putCard(putPatterns[randNum], 0, True)#カードを出す処理。Noneの場合は一枚引く
        dealer.skipPlayer()#自分の次の人の番にする
        tryNum[randNum] += 1#試行回数を増やす
        scoreSum[randNum] += dealer.gameStart()#プレイアウト。返り値は自分のスコア

        break #debug
        if time.perf_counter() - startTime > 4: #4秒超えたら終わり
            break

    print('結果')
    for i in range(len(putPatterns)):
        scoreMean[i] = scoreSum[i] / tryNum[i]
        print(str(putPatterns[i]) + 'を出したときのスコアの平均' + str(int(scoreMean[i])))

    maxIndex = scoreMean.index(max(scoreMean))
    ansCard = putPatterns[maxIndex]

    print('play out num is')
    print(counter)


    if ansCard is None:
        return None
    
    card = {}
    card['color'] = ansCard.get('color')
    if ansCard.get('special') is not None:
        card['special'] = ansCard.get('special')
    else:
        card['number'] = ansCard.get('number')

    print('selected card is')
    print(card)
    print(ansCard.get('selectColor'))

if __name__ == '__main__':
    main()
