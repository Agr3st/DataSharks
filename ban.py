import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import Toplevel

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from copy import deepcopy
from datetime import datetime
import numpy as np
from datetime import date, timedelta
from calendar import monthrange
from pyswarm import pso

#kolorki ii czcionki itp do gui
click = "#70a0f0"
click2 = "#08a0e0"
f = ("Arial", 12)

#parametry swarm optimalization (mozna zmieniac)
price_range = range(10, 300, 1)
max_iterations = 50        
swarm_size = 30            
omega=0.9                  
phip=0.45                  
phig=0.45



#ladowanie modelu i danych
model = xgb.XGBRegressor()
model.load_model('model.json') 

data = pd.read_csv( 'data/axe_transactions_with_elasticity_corrected.csv' )
data[ 'transaction_datetime' ] = pd.to_datetime( data[ 'transaction_datetime' ] )
data[ 'day_of_year' ] = data[ 'transaction_datetime' ].dt.dayofyear

###
today = date.today()
_, last_day_of_month = monthrange( today.year, today.month )
start_date = today
end_date = today.replace( day = last_day_of_month )

label_encoder = LabelEncoder()
L = sorted(list(set(data['product_name'])))
data[ 'location' ] = label_encoder.fit_transform( data[ 'location' ] )
data[ 'product_name' ] = label_encoder.fit_transform( data[ 'product_name' ] )
product_mapping = dict(zip(L, data['product_name']))

X = data[ [ 'unit_price', 'discount' ] ]
y = data[ 'quantity' ]

X_train, X_test, y_train, y_test = train_test_split( X, y, test_size = 0.2, random_state = 42 )

def objective_function(price, data, product_name, cost, start_date, end_date):
    predicted_profits = predict_profits_future(data, product_name, price[0], cost, start_date, end_date)
    return -predicted_profits 

def find_optimal_price(data, product_name, cost, start_date, end_date, price_range, maxiter=100, swarmsize=30, omega=0.5, phip=0.5, phig=0.5):
    # PSO parameters
    lb = [np.min(price_range)]
    ub = [np.max(price_range)]

    optimal_price, max_profits = pso(objective_function, lb, ub, args=(data, product_name, cost, start_date, end_date), maxiter=maxiter, swarmsize=swarmsize, omega=omega, phip=phip, phig=phig)

    return optimal_price[0], -max_profits  # Return the optimal price and maximized profits

def predict_profits_future(data, product_name, new_price, cost, start_date, end_date):
    future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    future_data = pd.DataFrame({
        'transaction_datetime': future_dates,
        'product_name': product_name,
        'unit_price': new_price,
        'discount': 0, 
        'quantity': np.nan, 
        'cost_price': cost,
        'profit': np.nan
    })
    
    new_quantity_predictions = model.predict(future_data[['unit_price', 'discount']])
    new_quantity_predictions = new_quantity_predictions.astype(int)

    future_data['quantity'] = new_quantity_predictions
    
    future_data['profit'] = (future_data['unit_price'] * future_data['quantity']) - (future_data['cost_price'] * future_data['quantity'])
    
    total_new_profits = future_data['profit'].sum()

    return total_new_profits

def on_close():
    if messagebox.askokcancel("Zamknij", "Czy na pewno chcesz wyjść?"):
        window.destroy()


def res():
    prod_name = combobox_prod.get()
    prod_encoded = product_mapping.get(prod_name, None)
    if prod_encoded is None:
        messagebox.showerror("Błąd", "Wybierz poprawny produkt.")
        return

    try:
        cost = float(entry_koszty.get())
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną cenę.")
        return

    optimal_price, max_profits = find_optimal_price(data, prod_name, cost, start_date, end_date, price_range, maxiter=max_iterations, swarmsize=swarm_size, omega=0.5, phip=0.5, phig=0.5)

    custom_msg("Wynik", f"Optymalna cena to: {optimal_price:.2f} \nMaksymalne przewidywane zyski: {max_profits:.2f}")

def custom_msg(title, message):
    #customowy okienko wiadomosciii
    msg_box = Toplevel()
    msg_box.title(title)
    msg_box.geometry("350x200") 

    msg_box.config(bg="#a0ffa0")

    label = tk.Label(msg_box, text=message, bg="#a0ffa0", font=("Helvetica", 12))
    label.pack(pady=20)

    button = tk.Button(msg_box, text="OK", command=msg_box.destroy, bg="#4CAF50", fg="white", font=("Helvetica", 10))
    button.pack(pady=10)

    msg_box.mainloop()

window = tk.Tk()
window.title("Formularz")
window.geometry("600x600")


window.state('zoomed')
window.configure(bg="#00a0f0")

title_label = ttk.Label(window, text="Optymalizator cen rynkowych", font=("Helvetica", 32, "bold"),background="#00a0f0")
title_label.pack(pady=20)


label_koszty = ttk.Label(window, text="Wprowadź koszty (w zł):",background=click,font=f)
label_koszty.pack(pady=5)
entry_koszty = ttk.Entry(window)
entry_koszty.pack(pady=5)

label_prod = ttk.Label(window, text="Wybierz produkt:",background=click,font=f)
label_prod.pack(pady=5)
opcje = list(product_mapping.keys())
combobox_prod = ttk.Combobox(window, values=opcje,background=click2,font=f)
combobox_prod.set("Wybierz...")
combobox_prod.pack(pady=5)

button = tk.Button(window, text="Wylicz optymalną cenę", command=res,background=click,font=f)
button.pack(pady=20)


window.protocol("WM_DELETE_WINDOW", on_close)


#window.attributes('-fullscreen',True)
window.mainloop()