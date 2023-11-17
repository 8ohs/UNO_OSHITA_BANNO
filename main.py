from Card import Card
from RandomPlayer import RandomPlayer
from Dealer import Dealer

def main():
    p1 = RandomPlayer(7)
    p2 = RandomPlayer(7)
    p3 = RandomPlayer(7)
    p4 = RandomPlayer(7)

    dealer = Dealer(p1, p2, p3, p4)
    dealer.gameStart()

if __name__ == '__main__':
    main()
