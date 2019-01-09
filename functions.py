#!/usr/bin/env python3
# Imports
import json, csv

# Load files
# Get NYSE stock symbols - row[0] for symbols
f = open('NYSE_SYMBOLS.csv')
csv_f = csv.reader(f)
# Get historical stock data
q = open('stocks.json')
stock_data = json.load(q)

# Constants
start_year = 2015
present = 2018
stock_price = 5.5
# Quarter
acceptable_percentage_of_overall_for_quarter = .7
acceptable_growth_for_quarter = .05
# Month
acceptable_percentage_of_overall_for_month = .33
acceptable_growth_for_month = .0166


# Gets all the historical data for a particular stock
def get_stock_data(stock):
    stock_rows = []
    for row in stock_data:
        if row["stock"] == stock and len(row["prices"]) > 0:
            stock_rows.append(row)
    return stock_rows

# Gets the date and returns month, day or year based on search specification
# Type = string; either month, day, year
def get_date(row, return_type):
    date = row["date"]
    month = date[:3]
    day = int(date[4:6])
    year = int(date[6:11])
    if return_type == "day":
        return day
    elif return_type == "month":
        return month
    elif return_type == "year":
        return year

# Gets quarterly data
def quarterly(quarter, year, stock):
    data = get_stock_data(stock)
    quarterly_data = []
    for row in data:
        if get_date(row, "year") == year:
            month = get_date(row, "month")
            if quarter == 1:
                if month == "Jan" or month == "Feb" or month == "Mar":
                    quarterly_data.append(row)
            elif quarter == 2:
                if month == "Apr" or month == "May" or month == "Jun":
                    quarterly_data.append(row)
            elif quarter == 3:
                if month == "Jul" or month == "Aug" or month == "Sep":
                    quarterly_data.append(row)
            elif quarter == 4:
                if month == "Oct" or month == "Nov" or month == "Dec":
                    quarterly_data.append(row)
    return quarterly_data

# Gets yearly data
def yearly(year, stock):
    data = get_stock_data(stock)
    yearly_data = []
    for row in data:
        if get_date(row, "year") == year:
            yearly_data.append(row)
    return yearly_data

# Gets monthly data
def monthly(month, year, stock):
    data = get_stock_data(stock)
    monthly_data = []
    for row in data:
        if get_date(row, "year") == year:
            if get_date(row, "month") == month:
                monthly_data.append(row)
    return monthly_data

# When calling any price function make sure to check if row['prices'] > 0
# Returns open price as a float
def get_open_price(row):
    price = row['prices'][0]
    if "," in price:
        price = price.replace(',', '')
    return float(price)

# Returns days highest price as a float
def get_high_price(row):
    price = row['prices'][1]
    if "," in price:
        price = price.replace(',', '')
    return float(price)

# Returns days lowest price as a float
def get_low_price(row):
    price = row['prices'][2]
    if "," in price:
        price = price.replace(',', '')
    return float(price)

# Returns closing price as a float
def get_close_price(row):
    price = row['prices'][3]
    if "," in price:
        price = price.replace(',', '')
    return float(price)

# Returns volume as an int
def get_volume(row):
    price = row['prices'][4]
    if "," in price:
        price = price.replace(',', '')
    return float(price)

# Changes calculation to percentages - used for display
def to_percent(x):
    percent = x * 100
    string = str(percent) + "%"
    return string

# Calculates growth over a period of time
def calc_growth(data):
    if len(data) > 0:
        last = data[0]
        first = data[len(data)-1]
        growth = (get_close_price(last) / get_close_price(first)) - 1
        return growth

# Calculates percent of total growth
#   Will do calculations based on absolute values, not positive vs negative
def percent_growth(small, big):
    if small is not None and big is not None:
        if abs(big) > 0:
            growth = (abs(small) / abs(big))
            return growth

# Compares the four quarters to the year
#   gets growth of quarter to year percentage and quarter percentage
def compare_quarters_to_year(year, stock):
    quarter_one = quarterly(1, year, stock)
    quarter_two = quarterly(2, year, stock)
    quarter_three = quarterly(3, year, stock)
    quarter_four = quarterly(4, year, stock)
    year_data = yearly(year, stock)
    year_growth = calc_growth(year_data)
    report = {1: {"to_year": percent_growth(calc_growth(quarter_one), year_growth), "quarterly": calc_growth(quarter_one)},
            2: {"to_year": percent_growth(calc_growth(quarter_two), year_growth), "quarterly": calc_growth(quarter_two)},
            3: {"to_year": percent_growth(calc_growth(quarter_three), year_growth), "quarterly": calc_growth(quarter_three)},
            4: {"to_year": percent_growth(calc_growth(quarter_four), year_growth), "quarterly": calc_growth(quarter_four)}}
    return report

# Does a loose check to see if any quarter has been more than min percent of year growth
def loose_check_for_seasonal():
    stocks = []
    for stock in csv_f:
        print(stock[0])
        average_1 = 0
        average_2 = 0
        average_3 = 0
        average_4 = 0
        average_1_counter = 0
        average_2_counter = 0
        average_3_counter = 0
        average_4_counter = 0
        for i in range((present - start_year)+1):
            compare = compare_quarters_to_year(start_year + i, stock[0])
            for x in compare:
                if compare[x]["to_year"] is not None:
                    if x == 1:
                        average_1 += float(compare[x]["to_year"])
                        average_1_counter += 1
                    elif x == 2:
                        average_2 += float(compare[x]["to_year"])
                        average_2_counter += 1
                    elif x == 3:
                        average_3 += float(compare[x]["to_year"])
                        average_3_counter += 1
                    elif x == 4:
                        average_4 += float(compare[x]["to_year"])
                        average_4_counter += 1
            if average_1_counter != 0:
                average_1 = average_1 / average_1_counter
            if average_2_counter != 0:
                average_2 = average_2 / average_2_counter
            if average_3_counter != 0:    
                average_3 = average_3 / average_3_counter
            if average_4_counter != 0:
                average_4 = average_4 / average_4_counter

            if average_1 > acceptable_percentage_of_overall_for_quarter or average_2 > acceptable_percentage_of_overall_for_quarter or average_3 > acceptable_percentage_of_overall_for_quarter or average_4 > acceptable_percentage_of_overall_for_quarter:
                if stock[0] not in stocks:
                    stocks.append(stock[0])
                    print(stocks)

# Checks a stocks last closing price against a specific cost
def check_all_for_price():
    stocks = []
    for stock in csv_f:
        print(stock[0])
        row = monthly('Dec', 2018, stock[0])
        if len(row) > 0:
            if get_close_price(row[len(row)-1]) < stock_price:
                stocks.append(stock[0])
    return stocks

print(check_all_for_price())
