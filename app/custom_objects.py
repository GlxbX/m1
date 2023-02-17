class Item:
    def __init__(self, id, name, price, qty, wanted_price=None):
        self.id = id
        self.name = name
        self.price = price
        self.qty = qty 
        self.wanted_price = wanted_price

    def __eq__(self, o):
        return [self.name, self.price] == [o.name, o.price]

    def __str__(self):
        return self.name + ' price - ' + str(self.price) + ' want - ' + str(self.wanted_price)

class Thing:
    def __init__(self, id, name, buy_price, wanted_sell_price):
        self.id = id
        self.name = name
        self.buy_price = buy_price
        self.wanted_sell_price = wanted_sell_price

