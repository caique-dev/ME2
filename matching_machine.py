# TODO remove redundance :( 
# TODO create pause/pause
# TODO Complete the implementation of the filled orders storage
# TODO pegged orders

class Utilities:
    @staticmethod
    def print_error(msg: str):
        Utilities.print_message('Error: ' + msg)

    @staticmethod
    def get_input(msg: str):
        return input('<< ' + msg + ': ')

    @staticmethod
    def print_message(msg: str):
        print('>> ' + msg)

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        # setting type
        if (
            order_dict['type'] == 'market' or 
            order_dict['type'] == 'limit' or
            'peg' in order_dict['type']
        ):
            if ('peg' in order_dict['type']):
                self.type = 'pegged'
            else:
                self.type = order_dict['type']
        else:
            Utilities.print_error('This order has an invalid type.')
            return None

        # setting side
        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                Utilities.print_error('This order has an invalid "side".')
                return None
        self.side = order_dict['side']
        
        # setting price
        if (self.type == "limit"):
            if (order_dict['price'] <= 0):
                Utilities.print_error('This order has an invalid price.')
                return None

            self.price = order_dict['price']

        # setting quantity        
        if (order_dict['qty'] <= 0):
                Utilities.print_error('This order has an invalid quantity.')
                return None
        
        self.qty = order_dict['qty']
    
    def __str__(self) -> str:
        print_msg = '(ID: {}) {} {} {}{}'.format(
                self.get_id(),
                self.get_type(),
                self.get_side(),
                self.get_qty(),
                " @ $" + str(self.get_price()) if self.type == 'limit' else ''
            )

        return print_msg
    
    def __repr__(self):
        return '(#{}) {} {} {} {}'.format(
            self.id,
            self.type,
            self.side,
            self.qty,
            '$'+str((self.price)) if (self.type == 'limit') else ('')
        )
    
    def set_id(self, id: int):
        self.id = id

    def get_id(self) -> int:
        return self.id

    def get_qty(self) -> int:
        return self.qty

    def set_qty(self, qty: int):
        if (qty > 0 and qty.is_integer()):
            self.qty = qty
        else:        
            Utilities.print_error('The new quantity is invalid.')

    def get_side(self) -> str:
        return self.side

    def get_price(self):
        if (self.type == 'pegged'):
            if (self.side == 'buy'):
                return OrderBook.get_bid_price()
            else:
                return OrderBook.get_offer_price()
        else:
            return self.price

    def set_price(self, price: float):
        if (price > 0):
            self.price = price
        else: 
            Utilities.print_error('The new price is invalid.')

    def get_type(self) -> str:
        return self.type

    def is_buy_order(self) -> bool:
        return (self.side == 'buy')

    def is_limit_order(self) -> bool:
        return (self.type == 'limit')

class OrderBook:
    # static atributes for pegged orders
    bid_price = 0 # highest buy price
    offer_price = 0 # lowest sell price

    def get_bid_price() -> float:
        return OrderBook.bid_price
    
    @staticmethod
    def update_bid_price(value: float):
        OrderBook.bid_price = value

    def get_offer_price() -> float:
        return OrderBook.offer_price
    
    @staticmethod
    def update_offer_price(value: float):
        OrderBook.offer_price = value

    def __init__(self):
        self.order_index = 0
        
        self.buy_side_dict = {}
        self.sell_side_dict = {}
        self.all_orders_dict = {}
        self.filled_orders_dict = {}

    def add_order(self, order: Order):
        if (order.is_buy_order()):
            order.set_id(self.get_last_order_id())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_order_index()
        else:
            order.set_id(self.get_last_order_id())
            self.sell_side_dict[order.get_id()] = order
            self.incremment_order_index()

        # updating the offer/bid price
        if (order.is_limit_order()):
            order_price = order.get_price()

            if (
                order.is_buy_order() and
                (
                    order_price > OrderBook.get_bid_price()
                )
            ):
                OrderBook.update_bid_price(order_price)
            
            if (
                (not order.is_buy_order()) and
                (
                    order_price < OrderBook.get_offer_price()
                )
            ):
                OrderBook.update_offer_price(order_price)


        self.all_orders_dict[order.get_id()] = order
        Utilities.print_message('Created the order: {}'.format(order))

    def cancel_order(self, id: int) -> Order:
        order = self.get_order(id)

        if not (order):
            Utilities.print_error('This order not exists.')
        else:
            # removing the order from the general dict
            del self.all_orders_dict[id]

            # removing the order from one of two specific  dict
            if (order.is_buy_order()):
                del self.buy_side_dict[id]
                return order
        
        del self.sell_side_dict[id]
        return order

    def change_order(self, id: int, new_price: str = '', new_qty: str = '', remove_priority: bool = True) -> bool:
        if not (self.order_exists(id)):
            Utilities.print_error('This order not exists.')
            return False
        else: 
            order = self.get_order(id)

            # updating the order's info
            if (new_price):
                order.set_price(int(new_price))
            if (new_qty):
                order.set_qty(int(new_qty))
            
            # removing the priority
            if (remove_priority):
                self.cancel_order(order.id)       
                self.all_orders_dict[order.id] = order

                if (order.is_buy_order()):
                    self.buy_side_dict[order.id] = order
                else:
                    self.sell_side_dict[order.id] = order
            
            return True

    def add_filled_order(self, order_id: int):
        self.filled_orders_dict[order_id] = self.get_order(order_id)

    def get_last_order_id(self):
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
        _str = 'Buy Orders: \n'
        for order in self.buy_side_dict:
            _str += str(self.buy_side_dict[order]) + '\n'

        _str += 'Sell Orders: \n'
        for order in self.sell_side_dict:
            _str += str(self.sell_side_dict[order]) + '\n'
        
        return _str

    def get_order(self, id: int) -> Order:
        if (id in self.all_orders_dict):
            return self.all_orders_dict[id]
        
        return None
    
    def get_all_orders(self) -> dict:
        return self.all_orders_dict

    def get_buy_orders(self) -> dict:
        return (self.buy_side_dict)
    
    def get_sell_orders(self) -> dict:
        return (self.sell_side_dict)

    def order_exists(self, id: int) -> bool:
        return (id in self.all_orders_dict)

class MatchingMachine:
    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order: str) -> Order:
        order_arr = (order.strip()).split(' ')

        # orders atributes
        if (len(order_arr) == 4):
            # join the pegged orders atributes
            if ('peg' in order_arr[0]):
                order_dict = {
                    'type': order_arr[0],
                    'side': order_arr[2],
                    'qty': int(order_arr[3])
                }

                pegged_type = order_arr[1] 
                if (pegged_type == 'bid'):
                    order_dict['price'] = OrderBook.get_bid_price()
                else:
                    order_dict['price'] = OrderBook.get_offer_price()

            # join the limit order atributes
            else:
                order_dict = {
                    'type': order_arr[0],
                    'side': order_arr[1],
                    'price': float(order_arr[2]),
                    'qty': int(order_arr[3])
                }
        
        # join the market order atributes
        elif (len(order_arr) == 3):
            order_dict = {
                'type': order_arr[0],
                'side': order_arr[1],
                'price': float(order_arr[2]),
                'qty': int(order_arr[3])
            }
        else:
            return None
        
        order_obj = Order(order_dict)

        if (order_obj):
            self.book.add_order(order_obj)
        
        return order_obj

    def add_filled_order(self, order_id: int):
        self.book.add_filled_order(order_id)

    def partial_trade(self, sell_order_id: int, buy_order_id: int):
        sell_order = self.get_order(sell_order_id)
        sell_qty = sell_order.get_qty()
        
        buy_order = self.get_order(buy_order_id)
        buy_qty = buy_order.get_qty()

        if (sell_qty < buy_qty):
            # the sell order has been filled
            new_buy_qty = buy_qty - sell_qty

            # changing the buy order qty
            self.book.change_order(
                buy_order.get_id(), 
                new_qty = new_buy_qty,
                remove_priority=False
            )

            # removing the filled order of the book
            filled_order = self.book.cancel_order(sell_order.get_id())
        else:
            # buy order has been filled
            new_sell_qty = sell_qty - buy_qty

            # changing the sell order qty
            self.book.change_order(
                sell_order.get_id(), 
                new_qty = new_sell_qty,
                remove_priority=False
            )
            # removing the filled order of the book
            filled_order = self.book.cancel_order(buy_order.get_id())

        self.book.add_filled_order(filled_order.get_id())

    def buy_limit_order(self, id: int) -> bool:
        buy_order_target = self.get_order(id)
        for sell_order in self.book.get_sell_orders():
            sell_order = self.get_order(sell_order)
            # this order is executed if the sell price is equal to or lower than the desired buy price
            if (sell_order.get_price() <= buy_order_target.get_price()):
                # getting the lowest price between the orders 
                trade_price = min(sell_order.price, buy_order_target.price)

                # setting the quantity that was traded
                if (sell_order.get_qty() >= buy_order_target.get_qty()):
                    trade_qty = buy_order_target.get_qty()  
                else: 
                    trade_qty = sell_order.get_qty()

                Utilities.print_message('Trade, price: {}, qty: {}'.format(trade_price, trade_qty))

                # partial trade
                if (buy_order_target.get_qty() != sell_order.get_qty()):
                    self.partial_trade({
                        'sell_order_id': sell_order.get_id(),
                        'buy_order_id': buy_order_target.get_id()
                    })

                    # sinaling if the target order was filled
                    return (buy_order_target.get_qty() > sell_order.get_qty())
                else:
                    # target order was filled executed
                    return False
        else:
            # none of the sell orders hit the price
            return False

    def sell_limit_order(self, id: int) -> bool:
        sell_order_target = self.get_order(id)
        for buy_order_id in self.get_buy_orders():
            buy_order = self.get_order(buy_order_id)

            # this order is executed if the buy price is equal to or greater than the desired sell price
            if (buy_order.get_price() >= sell_order_target.get_price()):
                # getting the highest value between the orders 
                trade_price = max(sell_order_target.get_price(), buy_order.get_price())

                # setting the quantity that was traded
                if (sell_order_target.get_qty() <= buy_order.get_qty()):
                    trade_qty = sell_order_target.get_qty()
                else: 
                    trade_qty = buy_order.get_qty()

                Utilities.print_message('Trade, price: {}, qty: {}'.format(trade_price, trade_qty))

                # partial trade
                if (buy_order.get_qty() != sell_order_target.get_qty()):
                    self.partial_trade(
                        sell_order_id= sell_order_target.get_id(),
                        buy_order_id= buy_order.get_id()
                    )
                    # sinaling if the target order was filled
                    return (sell_order_target.get_qty() > buy_order.get_qty())
                else:
                    # order was completly executed
                    return False
            
        # none of the buy orders hit the price
        return False
            
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
            
            Utilities.print_message('Trade, price: {}, qty: {}'.format(trade_qty, trade_price))

            # partial trade
            if (buy_order_target.get_qty() != sell_order.get_qty()):
                self.partial_trade(
                    sell_order_id= sell_order.get_id(),
                    buy_order_id= buy_order_target.get_id()
                )

                # sinaling if the target order was filled
                return (buy_order_target.get_qty() > sell_order.get_qty())
            else:
                # target order was completly filled
                return False
        else:
            # there are no more sell ordes
            return False

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
            
            Utilities.print_message('Trade, price: {}, qty: {}'.format(trade_qty, trade_price))

            # partial trade
            if (sell_order_target.get_qty() != buy_order.get_qty()):
                self.partial_trade(
                    buy_order_id = buy_order.get_id(),
                    sell_order_id = sell_order_target.get_id()
                )

                # sinaling if the target order was filled
                return (sell_order_target.get_qty() > buy_order.get_qty())
            else:
                # the order was completly filled
                return False
        else:
            # there are no more buy ordes
            return False
        
    def get_sell_orders(self):
        return (self.book.get_sell_orders())

    def get_buy_orders(self):
        return (self.book.get_buy_orders())

    def get_order(self, id: int):
        return self.book.get_order(id)

    def cancel_order(self, id: int) -> Order:
        order = self.book.cancel_order(id)
        if (order):
            Utilities.print_message('Order cancelled: {}'.format(order))

        return order

    def change_order(self, id: int, new_price: int = 0, new_qty: int = 0) -> bool:
        self.book.change_order(id, new_price, new_qty)

    def order_exists(self, id: int) -> bool:
        return self.book.order_exists(id)

    def try_execute_order(self, id: int) -> bool:
        if (self.order_exists(id)):
            order = self.get_order(id)
            try_execute_order_again = False
            # make trade
            if (order.is_buy_order()):
                if (order.is_limit_order()):
                    try_execute_order_again = self.buy_limit_order(id)
                else:
                    try_execute_order_again = self.buy_market_order(id)
            else:
                if (order.is_limit_order()):
                    try_execute_order_again = self.sell_limit_order(id)
                else:
                    try_execute_order_again = self.sell_market_order(id)

            if (try_execute_order_again):
                # trying to fill the current order
                self.try_execute_order(order)
        else:
            return False

        return True

    def manual_input_handler(self):
        MatchingMachine.help()
        Utilities.print_message('Enter your orders/commands line by line or comma separated:')
        while (True):
            prompt_input_arr = input('<< ').split(',')

            for command in prompt_input_arr:
                if ('print' in command):
                    print(self.book)
                
                elif ('cancel' in command):
                    cmd_arr = command.split(' ')
                    if (cmd_arr[2].isdigit()):
                        self.cancel_order(int(cmd_arr[2]))
                    else:
                        Utilities.print_error('Invalid ID.')
                
                elif ('change' in command):
                    cmd_arr = command.split(' ')
                    if (cmd_arr[-1].isdigit()):
                        if (self.book.order_exists(int(cmd_arr[-1]))):
                            order_id = int(cmd_arr[-1])
                        else:
                            Utilities.print_error('This order not exists.')
                    else:
                        Utilities.print_error('This ID is invalid')

                    new_price = Utilities.get_input('Enter the new price (press Enter to keep it unchanged)')            
                    new_qty = Utilities.get_input('Enter the new quantity (press Enter to keep it unchanged)')            
                    
                    old_order = self.book.get_order(order_id)
                    # Changing the order without losing its priority
                    self.book.change_order(
                        order_id,
                        new_price=new_price,
                        new_qty=new_qty
                    )
                    new_order = self.get_order(order_id)
                    Utilities.print_message('Order changed: {} -> {}'.format(old_order, new_order))

                elif ('exit' in command):
                    Utilities.print_message('Ending the program...')
                    break
                
                elif ('help' in command):
                    MatchingMachine.help()

                elif ('skip' in command):
                    pass

                # create a new order
                else:
                    order = self.add_order(command)
                    
                    if (order):
                        self.try_execute_order(order.get_id())
                    else:
                        Utilities.print_error('"{}", is an invalid and has been ignored.'.format(command))
    
    @staticmethod
    def help():
        Utilities.print_message('To add a new order: create order <order type (limit/market/pegged)> <order price (just for limit orders)> <order quantity>')
        Utilities.print_message('To change an order: create <order id>')
        Utilities.print_message('To cancel an order: cancel <order id>')
        Utilities.print_message('To print the book: print book')
        Utilities.print_message('To exit the program: exit')


        

primary_book = OrderBook()
machine = MatchingMachine(primary_book)

primary_book.add_order(Order({'type': 'limit', 'side': 'buy', 'price': 11, 'qty': 10}))

machine.manual_input_handler()
# machine.add_order({'type': 'market', 'side': 'sell', 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 9, 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 180, 'qty': 19})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 160, 'qty': 15})

# print(current_order)

# print(primary_book.get_buy_order())
# print(primary_book.get_sell_order())