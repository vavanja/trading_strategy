import pandas as pd
import matplotlib.pyplot as plt


def get_btc_data():
    return pd.read_csv('3month_1hour.csv')


def calculate_buy_positions(initial_number: int) -> list:
    percentage_decreases = [2, 4, 4, 6, 6]
    current_number = initial_number
    decreased_numbers = [initial_number, ]
    for percentage_decrease in percentage_decreases:
        current_number = current_number * (1 - percentage_decrease / 100)
        decreased_numbers.append(round(current_number, 1))
    return decreased_numbers


def get_my_order_book(buy_orders: list, budget: int) -> list:
    order_book = []
    for count, order in enumerate(buy_orders):
        order_info = {
            'name': f'Position №{count}',
            'buy_price': order,
            'sell_price': round(order + (order * 0.05), 1),
            'status': 'waiting',
            'bid': round(budget / len(buy_orders), 2),
            'profit': 0,
            'date_buy': [],
            'date_sell': [],
            'max_drawdown': 0,
        }
        order_book.append(order_info)
    return order_book


async def calculate_results(my_order_book, budged):
    min_budget = []
    max_budget = [budged]
    profitable = 0
    profit = 0
    for o in my_order_book:
        d = o['bid'] - ((o['bid'] * o['max_drawdown']) / 100)
        max_budget.append(o['profit'])
        min_budget.append(d)
        if o['profit'] > 0:
            profitable += 1
            profit += o['profit']

    max_drawdown = round(((sum(min_budget) - sum(max_budget)) / sum(max_budget)) * 100, 2)

    return profitable, profit, max_drawdown


async def check_to_but_or_sell(orders: list, btc_price_buy, btc_price_sell, date, sender: tuple, budged):
    bot, msg = sender
    current_budget = []
    # drawdown = 0
    # drawup = 0

    for order in orders:
        if order['status'] != 'closed':
            if order['status'] == 'waiting':
                if -20 < order['buy_price'] - btc_price_buy < 40:
                    await bot.send_message(msg.chat.id, f'🟢 Buy BTC 🟢 \n Order name: {order["name"]} \n Date: {date} \n Price: {btc_price_buy}$')
                    order['status'] = 'open'
                    order['date_buy'] += [date]
                current_budget.append(order['bid'])
                continue

            if order['status'] == 'open':
                avg = (btc_price_buy+btc_price_sell)/2

                # берем середнє число для реалістичності просадки
                if order['buy_price'] > avg:

                    #розрахунок просадки
                    drawdown = round(((order['buy_price'] - avg) / (order['buy_price'])) * 100, 3)

                    # розрахунок бюджета за годину якщо ціна нище поточної ціни входу
                    current_budget.append(order['bid'] - ((order['bid'] * drawdown) / 100))

                    if order['max_drawdown'] == 0 or order['max_drawdown'] < drawdown:
                        order['max_drawdown'] = drawdown
                else:

                    drawup = round(((avg - order['buy_price']) / avg) * 100, 3)
                    # розрахунок бюджета за годину якщо ціна вище поточної ціни входу
                    current_budget.append(order['bid'] + ((order['bid'] * drawup) / 100))

                if - 10 < (order['sell_price'] - btc_price_sell) < 20:
                    await bot.send_message(msg.chat.id, f'🛑 Sell BTC 🛑 \n Order name: {order["name"]} \n Date: {date} \n Price: {btc_price_sell}$')

                    order['status'] = 'closed'
                    order['date_sell'] += [date]
                    order['profit'] += round(order['bid'] * 0.05 * (order['sell_price'] / btc_price_sell), 2)

        else:
            current_budget.append(order['profit'] + order['bid'])

    return sum(current_budget) or budged


async def trade_strategy(budged=None, start_price=None, sender: tuple = None):
    bot, msg = sender
    df = get_btc_data()

    #рахуємо ордери на покупку\продаж
    buy_orders = calculate_buy_positions(start_price)

    #створюємо ордери
    my_order_book = get_my_order_book(buy_orders, budged)

    calc_budget = []                                            #погодинна сума капіталу

    for index, row in df.iloc[::-1].iterrows():
        current_budged = await check_to_but_or_sell(orders=my_order_book, btc_price_buy=row['low'], btc_price_sell=row['high'], date=row['date'], sender=sender, budged=budged)
        calc_budget.append((row['date'], current_budged))

    profitable, profit, max_drawdown = await calculate_results(my_order_book, budged)

    text = f"Total bids: {len(my_order_book)} \n Profitable bids: {profitable} \n Unprofitable bids: {len(my_order_book) - profitable} \n Total profit from {budged}$ => {round((profit / budged) * 100, 2)}% ({profit}$) \n Max drawdown: {max_drawdown}%"
    await bot.send_message(msg.chat.id, text)

    df = pd.DataFrame(calc_budget, columns=['date', 'budget'])
    plt.grid(True)
    plt.plot(df['date'], df['budget'], color='red')

    plt.title('Budget Change')
    plt.xlabel('Date')
    plt.ylabel('Budget')

    plt.xlim(left=min(df['date']), right=max(df['date']))
    plt.ylim(bottom=min(df['budget']), top=max(df['budget']))
    filename = f'trading_strategy_user_#{msg.from_user.id}.png'
    plt.savefig(f'plots/{filename}')
    await bot.send_message(msg.chat.id, 'Sending budget report....')
    with open(f'plots/{filename}', 'rb') as f:
        await bot.send_photo(msg.chat.id, f)

    await bot.send_message(msg.chat.id, 'Changing budget per hour')
    # plt.show()


async def main(sender: tuple):
    # day_start = '2022-09-15 00:00:00'
    # day_end = '2023-01-15 00:00:00'
    start_price = 20000
    budget = 50000
    await trade_strategy(budged=budget, start_price=start_price, sender=sender)

