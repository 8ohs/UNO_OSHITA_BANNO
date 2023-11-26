from RandomPlayer import RandomPlayer
from Dealer import Dealer
import random

def main():
    #before_card = {'color' : 'yellow', 'number' : 9} #場のカード
    before_card = {'color' : 'green', 'number' : 9} #場のカード
    playersCardNum = [2, 7, 7] # リバースされてないときの順番で自分の次の人から
    releasedCards = [{'color' : 'green', 'number' : 0}, {'color' : 'red', 'number' : 0}, {'color' : 'green', 'number' : 1}] # すでに出されたカードリスト
    cards = [{'color' : 'green', 'number' : 1}, {'color' : 'red', 'number' : 1}, {'color' : 'red', 'number' : 8}, {'color' : 'black', 'special' : 'wild_draw_4'}, {'color' : 'red', 'special' : 'skip'}, {'color' : 'red', 'special' : 'draw_2'}] # 自分の手札
    isReverse = False #リバース中かどうか (リバース中ならTrue)

    # ここで手札とbefore_cardから合法手を選ぶ処理をする
    
    gouhousyu = [{'color' : 'green', 'number' : 1}, {'color' : 'black', 'special' : 'wild_draw_4'}] # 合法手
    #gouhousyu = [{'color' : 'black', 'special' : 'wild_draw_4'}] # 合法手
    
    putPatterns = [] #色選択を考慮した出す手の全パターン
    for c in gouhousyu:
        if (c.get('special') == 'wild' or
            c.get('special') == 'wild_draw_4'):
            for selectColor in ['red', 'blue', 'green', 'yellow']:
                card = {'color' : 'black', 'special' : c.get('special'), 'selectColor' : selectColor}
                putPatterns.append(card)
        else:
            putPatterns.append(c)

    putPatterns.append(None) #戦略的パス
                 
    tryNum = [0] * len(putPatterns) #試行回数
    scoreSum = [0] * len(putPatterns) #総得点 (勝利数にしたほうがいいか相談)
    scoreMean = [0] * len(putPatterns) #得点の平均

    p1 = RandomPlayer(0) #自分の分身
    p2 = RandomPlayer(playersCardNum[0])
    p3 = RandomPlayer(playersCardNum[1])
    p4 = RandomPlayer(playersCardNum[2])

    playOutNum = 5000 #プレイアウト数

    for i in range(playOutNum):
        randNum = random.randrange(len(putPatterns))#乱数生成
        selectedCard = putPatterns[randNum] #選ばれたカード
        dealer = Dealer(p1, p2, p3, p4)
        dealer.removeCardsFromYama(releasedCards, True) #山から出されたカードを抜く
        dealer.removeCardsFromYama(cards, False) #山から自分の手札のカードを抜く
        dealer.isReverse = isReverse #リバース中かどうかをセット
        dealer.cards[0] = cards.copy()#手札をセット
        dealer.beforeCard = before_card#場の一番上のカードをセット
        if selectedCard is not None and selectedCard.get('special') == 'wild_draw_4' and len(gouhousyu) != 1:#最初のみチャレンジが成功する場合必ずされる
            dealer.draw4Cards()
        else:
            dealer.putCard(putPatterns[randNum], 0, True)#カードを出す処理。Noneの場合は一枚引く
        dealer.skipPlayer()#自分の次の人の番にする
        tryNum[randNum] += 1#試行回数を増やす
        scoreSum[randNum] += dealer.gameStart()#プレイアウト。返り値は自分のスコア

    print('結果')
    for i in range(len(putPatterns)):
        scoreMean[i] = scoreSum[i] / tryNum[i]
        print(str(putPatterns[i]) + 'を出したときのスコアの平均' + str(int(scoreMean[i])))

if __name__ == '__main__':
    main()
