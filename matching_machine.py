# TODO remove prints from OrderBook methods
# TODO complete the trade methods (partial trade)
# TODO complete the unified trade order method
# TODO implement input handling
# TODO implement the order executor

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        if (order_dict['type'] != 'market' and order_dict['type'] != 'limit'):
                print('This order has an invalid type.')
                return None
        self.type = order_dict['type']

        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                print('This order has an invalid "side".')
                return None
        self.side = order_dict['side']
        
        if (self.type == "limit"):
            if (order_dict['price'] <= 0):
                print('This order has an invalid price.')
                return None

            self.price = order_dict['price']

        if (order_dict['qty'] <= 0):
                print('This order has an invalid quantity.')
                return None
        
        self.qty = order_dict['qty']
    
    def __str__(self):
        print_msg = '(ID: {}) {} {} {} {}'.format(
                self.get_id(),
                self.get_type(),
                self.get_side(),
                self.get_qty(),
                "@ " + str(self.get_price()) if self.type == 'limit' else ''
            )

        return print_msg
    
    def __repr__(self):
        return '(#{}) {} {} {} {}'.format(self.id, self.type, self.side, self.price if self.type == 'limit' else '', self.qty)
    
    def set_id(self, id: int):
        self.id = id

    def get_id(self):
        return self.id

    def get_qty(self):
        return self.qty

    def set_qty(self, qty):
        if (qty > 0):
            self.qty = qty
            return
        
        print('The new quantity is invalid.')

    def get_side(self):
        return self.side

    def get_price(self):
        return self.price

    def set_price(self, price):
        if (price > 0):
            self.price = price
            return
        
        print('The new price is invalid.')

    def get_type(self):
        return self.type

    def is_buy_order(self) -> bool:
        return (self.side == 'buy')

    def is_limit_order(self) -> bool:
        return (self.type == 'limit')

class OrderBook:
    def __init__(self):
        self.order_index = 0
        
        self.buy_side_dict = {}
        self.sell_side_dict = {}
        self.all_orders_dict = {}

    def add_order(self, order: Order):
        if (order.is_buy_order()):
            order.set_id(self.get_last_order_id())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_order_index()
        else:
            order.set_id(self.get_last_order_id())
            self.sell_side_dict[order.get_id()] = order
            self.incremment_order_index()

        self.all_orders_dict[order.get_id()] = order
        print('Created the order: ', order)

    def cancel_order(self, id: int) -> Order:
        order = self.get_order(id)

        if not (order):
            print('This is an invalid ID.')
        else:
            # removing the order from the general dict
            del self.all_orders_dict[id]

            # removing the order from one of two specific  dict
            if (order.is_buy_order()):
                del self.buy_side_dict[id]
                return order
        
        del self.sell_side_dict[id]
        return order

    def change_order(self, id: int, new_infos: dict):
        if not (id in self.get_all_orders()):
            print('This is an invalid ID.')
            return None
        else: 
            order = self.get_order(id)

            # updating the order's info
            if ('price' in new_infos):
                order.set_price(new_infos['price'])
            if ('qty' in new_infos):
                order.set_qty(new_infos['qty'])
            
            # removing the priority
            self.cancel_order(order.id)             
            self.all_orders_dict[order.id] = order

            if (order.is_buy_order()):
                self.buy_side_dict[order.id] = order
            else:
                self.sell_side_dict[order.id] = order

    def get_last_order_id(self):
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
        _str = 'Buy Side: \n'
        for order in self.buy_side_dict:
            _str += str(self.buy_side_dict[order]) + '\n'

        _str += 'Sell Side: \n'
        for order in self.sell_side_dict:
            _str += str(self.sell_side_dict[order]) + '\n'
        
        return _str

    def get_order(self, id: int) -> Order:
        if (id in self.all_orders_dict):
            return self.all_orders_dict[id]
    
    def get_all_orders(self) -> dict:
        return self.all_orders_dict


        return None

    def get_buy_orders(self) -> dict:
        return (self.buy_side_dict)
    
    def get_sell_orders(self) -> dict:
        return (self.sell_side_dict)

    def order_exists(self, id: int) -> bool:
        return (id in self.all_orders_dict)

class MatchingMachine:
    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order: dict) -> Order:
        order_obj = Order(order)
        if (order_obj):
            self.book.add_order(order_obj)
        
        return order_obj

    def partial_trade(self, sell_order_id: int, buy_order_id: int):
        print('partial trade!')
        pass

    def buy_limit_order(self, id: int) -> bool:
        buy_order = self.get_order(id)
        for sell_order in self.book.get_sell_orders():
            sell_order = self.get_order(sell_order)
            # this order is executed if the sell price is equal to or lower than the desired buy price
            if (sell_order.get_price() <= buy_order.get_price()):
                # trade 
                trade_price = min(sell_order.price, buy_order.price)
                trade_qty = buy_order.get_qty() if (sell_order.get_qty() >= buy_order.get_qty()) else (sell_order.get_qty())

                print("Trade, price: {}, qty: {}".format(trade_price, trade_qty))

                # partial trade
                if (buy_order.get_qty() != sell_order.get_qty()):
                    self.partial_trade({
                        'sell_order_id': sell_order.get_id(),
                        'buy_order_id': buy_order.get_id()
                    })
                    return False
                else:
                    # order completely executed
                    return True

    def sell_limit_order(self, id: int) -> bool:
        sell_order_target = self.get_order(id)
        for buy_order_id in self.get_buy_orders():
            buy_order = self.get_order(buy_order_id)

            # this order is executed if the buy price is equal to or greater than the desired sell price
            if (buy_order.get_price() >= sell_order_target.get_price()):
                # trade 
                trade_price = max(sell_order_target.get_price(), buy_order.get_price())
                trade_qty = sell_order_target.get_qty() if (sell_order_target.get_qty <= buy_order.get_qty()) else (buy_order.get_qty())

                print("Trade, price: {}, qty: {}".format(trade_price, trade_qty))

                # partial trade
                if (buy_order.get_qty() != sell_order_target.get_qty()):
                    self.partial_trade(
                        sell_order_id= sell_order_target.get_id(),
                        buy_order_id= buy_order.get_id()
                    )
                    return False
                else:
                    # order completely executed
                    return True

    def buy_market_order(self, id: int) -> bool:
        buy_order_target = self.get_order(id)

        # generating an array from dict
        lower_price = []
        for order_id in self.get_sell_orders():
            sell_order = self.get_order(order_id)

            # removing market orders from the array
            if (sell_order.is_limit_order()):
                lower_price.append(sell_order)
        
        # sorting the array in ascending order            
        lower_price.sort(key = lambda order : order.price)

        # verifying if the array is not empty
        if (lower_price):
            sell_order = lower_price[0]
            trade_price = lower_price[0].get_price()
            if (buy_order_target.get_qty() <= sell_order.get_qty()):
                trade_qty = buy_order_target.get_qty()
            else:
                trade_qty = sell_order.get_qty()
            
            print_msg = 'Trade, price: {}, qty: {}'.format(trade_qty, trade_price)
            print(print_msg)

            # partial trade
            if (buy_order_target.get_qty() != sell_order.get_qty()):
                self.partial_trade(
                    sell_order_id= sell_order.get_id(),
                    buy_order_id= buy_order_target.get_id
                )
                return False
            else:
                return True

    def sell_market_order(self, id: int) -> bool:
        sell_order_target = self.get_order(id)

        # generating an array from dict
        highest_price = []
        for order_id in self.get_buy_orders():
            buy_order = self.get_order(order_id)

            # removing market orders from the array
            if (buy_order.is_limit_order()):
                highest_price.append(buy_order)
        
        # sorting the array in descending order
        highest_price.sort(key = lambda order : order.price, reverse=True)

        # verifying if the array is not empty
        if (highest_price):
            buy_order = highest_price[0]
            trade_price = highest_price[0].get_price()
            if (sell_order_target.get_qty() <= buy_order.get_qty()):
                trade_qty = sell_order_target.get_qty()
            else:
                trade_qty = buy_order.get_qty()
            
            print_msg = 'Trade, price: {}, qty: {}'.format(trade_qty, trade_price)
            print(print_msg)

            # partial trade
            if (sell_order_target.get_qty() != buy_order.get_qty()):
                self.partial_trade(
                    buy_order_id = buy_order.get_id(),
                    sell_order_id = sell_order_target.get_id
                )
                return False
            else:
                return True

    def get_sell_orders(self):
        return (self.book.get_sell_orders())

    def get_buy_orders(self):
        return (self.book.get_buy_orders())

    def print_book(self):
        print(self.book)

    def get_order(self, id: int):
        return self.book.get_order(id)

    def cancel_order(self, id: int) -> Order:
        order = self.book.cancel_order(id)
        if (order):
            print('Order cancelled: ', order)

        return order

    def change_order(self, id: int, new_infos: dict):
        self.book.change_order(id, new_infos)

    def order_exists(self, id: int) -> bool:
        return self.book.order_exists(id)

    def try_execute_order(self, id: int) -> bool:
        if (self.order_exists(id)):
            order = self.get_order(id)
            
            # make trade
            if (order.is_buy_order()):
                if (order.is_limit_order()):
                    partial_trade = self.buy_limit_order(id)
                else:
                    partial_trade = self.buy_market_order(id)
            else:
                if (order.is_limit_order()):
                    partial_trade = self.sell_limit_order(id)
                else:
                    partial_trade = self.sell_market_order(id)
        else:
            return False
        
        # partial trade
        if (partial_trade):
            self.partial_trade()

        return True

primary_book = OrderBook()
machine = MatchingMachine(primary_book)

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 10, 'qty': 10})

machine.add_order({'type': 'market', 'side': 'sell', 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 9, 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 180, 'qty': 19})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 160, 'qty': 15})

machine.try_execute_order(1)
# print(current_order)

# print(primary_book.get_buy_order())
# print(primary_book.get_sell_order())