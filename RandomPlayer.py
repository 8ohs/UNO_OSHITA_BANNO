import random

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
            # 場札と数字または記号が同じカード
                self.gouhousyu.append(card)

    def __init__(self, firstCardNum, removeCard):
        self.firstCardNum = firstCardNum # モンテカルロ開始するときの所持カード枚数
        self.gouhousyu = []
        self.removeCard = removeCard
