import sys
import datetime
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import seaborn as sns

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from urllib.request import urlopen, Request
import json

import pandas as pd
import numpy as np

category_list = ["Income", "Bills", "Food", "Travel", "Shopping", "Fun", "Misc", "Other"]

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

style.use("seaborn-talk")

f = Figure(figsize=(5, 5), dpi=100, constrained_layout=True)
a = f.add_subplot(111)


def update_menu(sel_menu, sel_opt):
    menu = sel_menu["menu"]
    menu.delete(0, "end")
    for string in sel_opt:
        menu.add_command(label=string,
                         command=lambda value=string: sel_menu.set(value))





def update_dict(key, dict):
    # print(str(dict))
    # print(key)
    # print(dict[key].get())
    if dict[key].get():
        # print("TRUE!")
        dict[key].set(0)
    else:
        # print("NOT TRUE!")
        dict[key].set(1)
    # print(dict[key].get())

# def popupfilters(self):



# def animate(i):
def quitt():
    exit()


# def update_data(filename):
#     #TODO


# Create Window for App
class Budgetapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Shareable Variables
        self.filename = ""
        self.dataframe = pd.DataFrame()
        self.account_dict = dict()
        self.category_dict = {cat: tk.IntVar(value=1, name=cat) for cat in category_list}
        self.budget_dict = {cat2: tk.DoubleVar(value=0, name=cat2+"-bgt") for cat2 in category_list}
        self.price_dict = pd.DataFrame()

        p1 = tk.Image('photo', file='wallet.png')

        # Setting icon of master window
        self.call('wm', 'iconphoto', self._w, p1)
        tk.Tk.wm_title(self, "Budget App")

        # Create container for window frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create dictionary of frames for later use
        self.frames = {}

        # Add all pages to dictionary
        for F in (StartPage, BudgetPage):
            frame = F(container, self)
            self.frames[F] = frame

            # make frame take up all space
            frame.grid(row=0, column=0, sticky="nsew")

        # show the starting page
        self.show_frame(StartPage)

    def show_frame(self, cont):
        # this function places desired frame on top
        frame = self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


# Create Start Page
def categorize_df(df):
    # Simplify Categories
    Food = ['Food & Dining', 'Restaurants', 'Fast Food', 'Groceries', 'Alcohol & Bars', 'Coffee Shops']
    Bills = ['Mortgage & Rent', 'Utilities', 'Mobile Phone', 'Home Insurance', 'Auto Insurance',
             'Bills & Utilities', 'Auto & Transport', 'Auto Payment', 'Service & Parts', 'Laundry',
             'Internet', 'Gas & Fuel', 'Insurance']
    Travel = ['Parking', 'Rental Car & Taxi', 'Air Travel', 'Hotel', 'Travel', 'Public Transportation']
    Fun = ['Movies & DVDs', 'Gift', 'Entertainment', 'Arts', 'Sports', 'Amusement']
    Income = ['State Tax', 'Income', 'Interest Income', 'Paycheck', 'Federal Tax']
    Shopping = ['Pharmacy', 'Shopping', 'Clothing', 'Electronics & Software', 'Business Services', 'Shipping',
                'Home Supplies', 'Home Improvement', 'Furnishings', 'Personal Care', 'Hobbies', 'Books', 'Music',
                'Office Supplies', 'Sporting Goods']
    Misc = ['Charity', 'Cash & ATM', 'Bank Fee', 'Doctor', 'Auto & Transport', 'ATM Fee', 'Printing', 'Dentist',
            'Student Loans', 'Education', 'Uncategorized', 'Health & Fitness', 'Pet Food & Supplies',
            'Home Services']

    df['Category2'] = ""

    # Add Overall Category (Category2) based on Category
    df.loc[df["Category"].str.contains("|".join(Food)), "Category2"] = "Food"
    df.loc[df["Category"].str.contains("|".join(Bills)), "Category2"] = 'Bills'
    df.loc[df["Category"].str.contains("|".join(Travel)), "Category2"] = 'Travel'
    df.loc[df["Category"].str.contains("|".join(Fun)), "Category2"] = 'Fun'
    df.loc[df["Category"].str.contains("|".join(Income)), "Category2"] = 'Income'
    df.loc[df["Category"].str.contains("|".join(Shopping)), "Category2"] = 'Shopping'
    df.loc[df["Category"].str.contains("|".join(Misc)), "Category2"] = 'Misc'

    # Leftover categories get added to Miscellaneous
    df.loc[df["Category2"] == "", "Category2"] = 'Other'

    return df


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Welcome", font=LARGE_FONT)
        # label.pack(pady=10, padx=10)
        label.grid(row=0, column=1)

        label_browse = tk.Label(self, text="Browse")
        label_browse.grid(row=1, column=0)

        self.edit_browse = tk.Entry(self)
        self.edit_browse.grid(row=1, column=1)

        button_load = ttk.Button(self, text="Load", command=self.load)
        button_load.grid(row=1, column=2)

        button_budget = ttk.Button(self, text="Budget", command=lambda: controller.show_frame(BudgetPage))
        button_budget.grid(row=2, column=1)

        self.load_text = tk.StringVar()
        label_load = tk.Label(self, textvariable=self.load_text)
        label_load.grid(row=3, column=1)

    def load(self):
        filename = askopenfilename(filetypes=[("Excel files", ".xlsx .xls .csv"), ("All Files", "*.*")],
                                   title="Select a file")

        self.edit_browse.delete(0, tk.END)
        self.edit_browse.insert(0, filename)

        # Determine if file is csv or xls
        if filename.endswith(".csv"):
            df = pd.read_csv(filename, parse_dates=True, index_col=0)
            df = categorize_df(df)
            self.load_text.set("CSV File has been loaded")
        elif filename.endswith(".xls") | filename.endswith(".xlsx"):
            df = pd.read_excel(filename, parse_dates=True, index_col=0)
            df = categorize_df(df)
            self.load_text.set("Excel File has been loaded")
        else:
            df = pd.Series()
            self.load_text.set("File type not supported")

        df = df.applymap(lambda s: s.lower() if type(s) == str else s)  # apply lowercase to all columns

        # Get sorted list of Account names
        account_list = df["Account Name"].unique()
        account_list = [ac.lower() for ac in account_list]
        account_list.sort()

        # Save File name, Dataframe, Max/min Prices
        self.controller.filename = filename
        self.controller.dataframe = df
        self.controller.price_dict = pd.DataFrame(data={"max": [df["Amount"].max()], "min": [df["Amount"].min()]})
        # Create dictionary for widget use later on
        self.controller.account_dict = {acct1: tk.IntVar(value=1, name=acct1) for acct1 in account_list}


class BudgetPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        start_lbl = tk.Label(self, text='Start')
        start_lbl.grid(row=1, column=0, columnspan=2, sticky="WE")
        end_lbl = tk.Label(self, text='End')
        end_lbl.grid(row=1, column=2, columnspan=2, sticky="WE")

        ##Dropdown for time range
        # Set list of options for month and year
        tod = datetime.datetime.today()  # today
        duration = (tod - datetime.timedelta(days=(6 * 31))).strftime("%Y-%m")
        str_date = duration.split("-")

        # TODO: Make years more dynamic
        years = list(range(2017, 2020, 1))  # initial default
        # years = self.controller.dataframe.sort_index().index.strftime("%Y").astype("int")
        self.opt_month = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November',
                          'December']
        self.opt_year = list(range(years[0], years[-1] + 1, 1))

        # Set default selections for drop down menus
        self.em_var = tk.StringVar(self)
        self.em_var.set(self.opt_month[-1])

        self.ey_var = tk.StringVar(self)
        self.ey_var.set(self.opt_year[-1])

        self.sm_var = tk.StringVar(self)
        self.sm_var.set(self.opt_month[int(str_date[1])])

        self.sy_var = tk.StringVar(self)
        self.sy_var.set(str_date[0])

        # Create Dropdown menus for start and end date
        self.startmonth_dd = tk.OptionMenu(self, self.sm_var, *self.opt_month)
        self.startyear_dd = tk.OptionMenu(self, self.sy_var, *self.opt_year)
        self.endmonth_dd = tk.OptionMenu(self, self.em_var, *self.opt_month)
        self.endyear_dd = tk.OptionMenu(self, self.ey_var, *self.opt_year)
        # Pack drop down menus
        self.startmonth_dd.grid(row=2, column=0, sticky="WE")  # pack(side=tk.LEFT, padx=2)
        self.startyear_dd.grid(row=2, column=1, sticky="WE")  # pack(side=tk.LEFT, padx=2)
        self.endmonth_dd.grid(row=2, column=2, sticky="WE")  # pack(side=tk.LEFT, padx=2)
        self.endyear_dd.grid(row=2, column=3, sticky="WE")  # pack(side=tk.LEFT, padx=2)

        # Button to select which filters to apply
        filterBtn = ttk.Button(self, text="Set Filters", command=lambda: self.popupfilters())
        filterBtn.grid(row=3, column=0, columnspan=2)  # pack(side=tk.RIGHT)

        # Drop Down menu to select which category to plot
        # TODO: Add dynamic drop down menu
        self.options = ["Income", "Bills", "Food", "Travel", "Shopping", "Fun", "Misc", "Other"]
        self.ddvar = tk.StringVar(self)
        self.ddvar.set(self.options[0])  # default value

        self.dropdown = tk.OptionMenu(self, self.ddvar, *self.options)
        self.dropdown.grid(row=3, column=2, columnspan=2)  # pack(side=tk.TOP) # side=tk.RIGHT

        # Button to plot category
        plot_button = ttk.Button(self, text="Plot",
                                 command=lambda: self.plot_data(self.canvas))
        plot_button.grid(row=3, column=4)  # pack()

        # Canvas to plot on
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=12, rowspan=16, padx=10,
                                    pady=10)  # pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)  # fill=tk.BOTH, , expand=True

        # Button to calculate budget
        budget_button = ttk.Button(self, text="Calculate Budget",
                                   command=self.budget_cal)
        budget_button.grid(row=2, column=13, columnspan=2)  # pack()

        r = 4
        for cat5 in self.controller.budget_dict.keys():
            tk.Label(self, text=cat5).grid(row=r, column=14)
            tk.Entry(self, textvariable=self.controller.budget_dict[cat5]).grid(row=r, column=15)
            r += 1


    def popupfilters(self):
        top = tk.Tk()
        top.wm_title("Filter Options")

        label = ttk.Label(top, text="Select which filters to apply", font=NORM_FONT)
        # label.pack(side="top", fill="x", pady=10)
        label.grid(row=0, column=0, padx=5, pady=5)

        # Accounts Filter
        accounts_label = tk.Label(top, text="Accounts: ", font=NORM_FONT)
        accounts_label.grid(row=1, column=0, sticky="W")

        r = 0
        row = 2
        # print("Account Loop")
        for acct in self.controller.account_dict.keys():
            chk = tk.Checkbutton(top, text=acct, variable=self.controller.account_dict[acct], onvalue=1, offvalue=0,
                                 command=lambda account_name=acct: update_dict(key=account_name,
                                                                               dict=self.controller.account_dict))
            # chk.select()
            if self.controller.account_dict[acct].get(): chk.select()
            chk.grid(row=row, column=r, pady=5, sticky="W")
            r += 1
            if r > 3:
                r = 0
                row = 3

        # Category Filters
        category_label = tk.Label(top, text="Categories: ", font=NORM_FONT)
        category_label.grid(row=row + 1, column=0, sticky="W")

        r = 0
        row += 2
        for cat1 in self.controller.category_dict.keys():
            chk = tk.Checkbutton(top, text=cat1, variable=self.controller.category_dict[cat1], onvalue=1, offvalue=0,
                                 command=lambda category=cat1: update_dict(key=category,
                                                                           dict=self.controller.category_dict))

            if self.controller.category_dict[cat1].get(): chk.select()
            chk.grid(row=row, column=r, pady=5, sticky="W")
            r += 1
            if r > 3:
                r = 0
                row += 1

        # Price Range Filter
        price_label = tk.Label(top, text="Price Range: ", font=NORM_FONT)
        price_label.grid(row=row + 1, column=0, sticky="W")

        min_label = tk.Label(top, text="Min")
        min_label.grid(row=row + 2, column=0, pady=5)

        top.min_entry = tk.Entry(top, text=str(self.controller.price_dict.loc[0, 'min']))
        top.min_entry.grid(row=row + 2, column=1, pady=5, sticky="W")

        max_label = tk.Label(top, text="Max")
        max_label.grid(row=row + 2, column=2, pady=5)

        top.max_entry = tk.Entry(top, text=str(self.controller.price_dict.loc[0, 'max']))
        top.max_entry.grid(row=row + 2, column=4, pady=5, sticky="W")

        okaybutton = ttk.Button(top, text="Okay", command=lambda: okayfun(self.controller, top=top))  # lambda: okayfun(top)
        okaybutton.grid(row=row + 3, column=3, padx=5, pady=5, sticky="W")

        def okayfun(cont, top):
            # update Price dictionary
            if not top.max_entry.get() == "":
                cont.price_dict["max"] = float(top.max_entry.get())
            if not top.min_entry.get() == "":
                cont.price_dict["min"] = float(top.min_entry.get())

            # # Verify Code is working
            # print("Max Price: " + str(cont.price_dict.loc[0, 'max']))
            # print("Min Price: " + str(cont.price_dict.loc[0, 'min']))
            # print(top.max_entry.get())
            # print(top.min_entry.get())

            #TODO: update OptionMenu for Categories
            # menu = BudgetPage.dropdown["menu"]
            # menu.delete(0, "end")
            # for string in BudgetPage.testdd:
            #     menu.add_command(label=string,
            #                      command=lambda value=string: BudgetPage.ddvar.set(value))
            # BudgetPage.update_option_menu(BudgetPage)

            top.destroy()

    def plot_data(self, canvas):
        # Clear axes
        a.clear()
        # Get selected category from dropdown
        selected_cat = self.ddvar.get()

        # Get duration from entry or dropdown
        # TODO: make duration user option
        start_month = self.sm_var.get()
        start_year = self.sy_var.get()
        start_str = start_month + " " + start_year
        start_date = datetime.datetime.strptime(start_str, '%B %Y')

        end_month = self.em_var.get()
        end_year = self.ey_var.get()
        end_str = end_month + " " + end_year
        end_date = datetime.datetime.strptime(end_str, '%B %Y')

        # Get filter settings
        account_dict = self.controller.account_dict
        category_dict = self.controller.category_dict
        accounts_on = [key for (key, value) in account_dict.items() if value.get() == 1]
        categories_on = [key.lower() for (key, value) in category_dict.items() if value.get() == 1]

        # Setup Dataframe
        temp_df = self.controller.dataframe.copy()
        # Apply Filters
        temp_df = temp_df[(temp_df['Account Name'].str.contains("|".join(accounts_on))) &
                          (temp_df['Category2'].str.contains("|".join(categories_on)))]
        # Groupby
        temp_df = temp_df.groupby([pd.Grouper(freq='M'), 'Category2'])['Amount']. \
            agg(['mean', 'sum', 'max']).sort_values(by=['Date', 'sum'], ascending=[True, False])
        temp_df = temp_df.reset_index(level='Category2')

        # Apply Date Duration
        temp_df = temp_df[(temp_df.index >= start_date) & (temp_df.index <= end_date)]
        # Extract only selected category
        temp = temp_df[temp_df['Category2'] == str(selected_cat).lower()]
        # Extract Selected Category from Dataframe for specified duration
        # temp = temp_df[(temp_df.index > duration) & (temp_df['Category2'] == str(selected_cat).lower())]
        # Set Date format for x-axis ticks
        temp.index = temp.index.strftime("%b %Y")

        # Plot data
        try:
            temp.plot(kind='bar', ax=a, rot=70)
            # Plot Average line
            a.axhline(y=temp['sum'].mean(), linestyle='--', color='r', label='Avg Sum')

            # Set rest of plot settings
            a.legend()
            a.set_xlabel('Month')
            a.set_ylabel('Cost ($)')
            a.set_title(selected_cat)
        except TypeError as e:
            a.text(0.35, 0.5, e, dict(size=25), wrap=True)
            a.axis("Off")

        plt.tight_layout()
        canvas.draw()

    def budget_cal(self):
        tod = datetime.datetime.today()  # today
        duration = (tod - datetime.timedelta(days=(6 * 31))).strftime("%Y-%m")
        df = self.controller.dataframe.copy()
        df = df[df.index > duration]

        # Caclulate averages
        income = df[(df['Category2'] == "income")].groupby(
            pd.Grouper(freq='M'))['Amount'].max().mean()
        avg_list = ['bills', 'food', 'travel', 'shopping', 'fun', 'misc', 'other']
        averages = []

        for item in avg_list:
            b = df[(df['Category2'] == item)].groupby(
            pd.Grouper(freq='M'))['Amount'].sum().mean()
            b *= 1.03  # add 3% margin
            averages.append(b)

        savings = income - sum(averages)

        budget_list = [income] + averages + [savings]

        r = 0
        for key in self.controller.budget_dict.keys():
            self.controller.budget_dict[key].set(value=round(budget_list[r], ndigits=2))
            r += 1




app = Budgetapp()
app.mainloop()
