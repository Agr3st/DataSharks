import pandas as pd
import random
from datetime import datetime, timedelta

n = 10000
start_date = datetime(2018, 1, 1)
end_date = datetime(2024, 6, 30)
categories = {
    'Hand Tools': ['Small Axe', 'Medium Axe'],
    'Outdoor Equipment': ['Large Axe'],
    'Combat Tools': ['Battle Axe']
}

axe_specs = {
    'Small Axe': {'size_cm': 35, 'weight_kg': 1.5, 'unit_price': 30, 'elasticity': -0.3},
    'Medium Axe': {'size_cm': 55, 'weight_kg': 3.0, 'unit_price': 50, 'elasticity': -0.4},
    'Large Axe': {'size_cm': 75, 'weight_kg': 6.0, 'unit_price': 80, 'elasticity': -0.5},
    'Battle Axe': {'size_cm': 95, 'weight_kg': 10.0, 'unit_price': 120, 'elasticity': -0.6}
}

payment_methods = ['Cash', 'Mobile Payment', 'Credit Card']
locations = range(15)


def random_date(start, end, transaction_num):
    current_date = start
    dates = []
    while len(dates) < transaction_num:
        daily_transactions = random.randint(8, 12)
        for _ in range(daily_transactions):
            time_of_day = timedelta(hours=random.randint(9, 18), minutes=random.randint(0, 59))
            dates.append(current_date + time_of_day)
            if len(dates) >= transaction_num:
                break
        current_date += timedelta(days=random.randint(1, 3))
    return dates[:transaction_num]


def generate_discount_schedule(start_date, end_date):
    discount_schedule = []
    current_date = start_date

    while current_date <= end_date:
        discount_duration = timedelta(weeks=random.randint(2, 4))
        discount_percentage = random.randint(5, 50)

        discount_start = current_date
        discount_end = discount_start + discount_duration

        if discount_end > end_date:
            discount_end = end_date
        discount_schedule.append((discount_start, discount_end, discount_percentage))

        no_discount_duration = timedelta(weeks=random.randint(8, 24))
        current_date = discount_end + no_discount_duration

    return discount_schedule


def get_discount_for_date(transaction_date, discount_schedule):
    for start, end, discount in discount_schedule:
        if start <= transaction_date <= end:
            return discount
    return 0


def generate_price_increase_schedule(start_date, end_date, base_price):
    price_schedule = []
    current_date = start_date
    current_price = base_price

    while current_date <= end_date:
        price_schedule.append((current_date, current_price))

        next_increase_duration = timedelta(weeks=random.randint(12, 24))
        current_date += next_increase_duration

        increase_percentage = random.uniform(1, 7)
        current_price = round(current_price * (1 + increase_percentage / 100), 2)

    return price_schedule


def get_price_for_date(transaction_date, price_schedule):
    for date, price in reversed(price_schedule):
        if transaction_date >= date:
            return price
    return price_schedule[0][1]


def simulate_quantity(base_quantity, price, base_price, discount, elasticity):
    price_change = (price - base_price) / base_price

    if price_change > 1.0:
        adjusted_quantity = 0
    elif price_change > 0.5:
        adjusted_quantity = base_quantity * (1 - 0.75)
    else:
        discount_effect = 1 + (discount / 50)
        adjusted_quantity = base_quantity * (1 + elasticity * price_change) * discount_effect

    return max(int(adjusted_quantity), 0)


discount_schedule = generate_discount_schedule(start_date, end_date)
transaction_dates = random_date(start_date, end_date, n)

price_increase_schedules = {axe: generate_price_increase_schedule(start_date, end_date, specs['unit_price']) for
                            axe, specs in axe_specs.items()}

data = []
for i in range(n):
    transaction_date = transaction_dates[i]
    customer_id = random.randint(20, 100)
    location = random.choice(locations)

    category = random.choice(list(categories.keys()))
    product_name = random.choice(categories[category])

    size_cm = axe_specs[product_name]['size_cm']
    weight_kg = axe_specs[product_name]['weight_kg']
    base_price = axe_specs[product_name]['unit_price']
    elasticity = axe_specs[product_name]['elasticity']

    unit_price = get_price_for_date(transaction_date, price_increase_schedules[product_name])
    discount = get_discount_for_date(transaction_date, discount_schedule)

    base_quantity = random.randint(5, 8)
    quantity = simulate_quantity(base_quantity, unit_price, base_price, discount, elasticity)
    total_amount = round(unit_price * quantity * (1 - discount / 100))
    cost_price = round(base_price * 0.4)
    profit = float( total_amount - (cost_price * quantity) )

    payment_method = random.choice(payment_methods)
    day_of_year = transaction_date.timetuple().tm_yday
    transaction_month = transaction_date.month
    transaction_year = transaction_date.year

    data.append([transaction_date, customer_id, location, product_name,
                 category, size_cm, weight_kg, quantity, unit_price, discount, total_amount,
                 payment_method, day_of_year, cost_price, profit, transaction_month, transaction_year])

columns = ['transaction_datetime', 'customer_id', 'location',
           'product_name', 'category', 'size_cm', 'weight_kg', 'quantity', 'unit_price',
           'discount', 'total_amount', 'payment_method', 'day_of_year', 'cost_price',
           'profit', 'transaction_month', 'transaction_year']

df = pd.DataFrame(data, columns=columns)

df.to_csv('axe_transactions_with_elasticity_corrected.csv', index=False)

print("Dataset wygenerowany i zapisany jako 'axe_transactions_with_elasticity_corrected.csv'.")
