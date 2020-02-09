import sys
import datetime
import calendar
import matplotlib
import matplotlib.pyplot as plt
import palettable.colorbrewer.qualitative as cb


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


text_font = {'family': 'serif',
        'weight': 'normal',
        'size': 8
        }

title_font = {'family': 'serif',
        'weight': 'bold',
        'size': 10
        }
figure_font = {'family': 'serif',
        'weight': 'heavy',
        'size': 12
        }

cat_path = r"C:\Users\xrchr\SynologyDrive\Desktop\Coding\Python\Projects\6_Money_Completed\DataSource\categories.csv"
categories_df = pd.read_csv(cat_path)
# category_list = ["Income", "Bills", "Food", "Travel", "Shopping", "Fun", "Misc", "Other"]
category_list = list(categories_df.columns)

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

style.use("seaborn-talk")

f = Figure(figsize=(5, 5), dpi=100, constrained_layout=False)
tod = datetime.datetime.today()  # today

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
def update_option_menu(op_menu, options, op_variables):
    op_menu['values'] = []
    titled_options = [x.title() for x in options]
    op_menu['values'] = titled_options
    op_menu.set(titled_options[0])
    # menu = op_menu["menu"]
    # menu.delete(0, "end")
    # for string in options:
    #     menu.add_command(label=string.title(),
    #                      command=lambda value=string.title(): op_variables.set(value))


# def animate(i):
def quitt():
    exit()


# Create Window for App
class Budgetapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Shareable Variables
        self.filename = ""
        self.dataframe = pd.DataFrame()
        self.account_dict = dict()
        self.category_dict = {cat: tk.IntVar(value=1, name=cat) for cat in category_list}
        self.budget_dict = {cat2: tk.DoubleVar(value=0, name=cat2 + "-bgt") for cat2 in category_list}
        self.budget_dict.update({"Savings": tk.DoubleVar(value=0, name="Saving-bgt")})
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
    # Add column Category2 - Parent Category
    df["Parent-Cat"] = ""
    df['Category2'] = ""
    # Remove Credit Card Payments and money transfers, due to redundancy
    drop_mask1 = (df["Category"] != "Credit Card Payment") & (df["Category"] != "Transfer")
    df = df.loc[drop_mask1].copy()

    # Organize into Parent Category
    for column in category_list:
        col = list(categories_df[column].dropna())
        df.loc[df["Category"].str.contains("|".join(col)), "Parent-Cat"] = column

    # Leftover categories get added to Miscellaneous
    df.loc[df["Parent-Cat"] == "", "Parent-Cat"] = 'Uncategorized'

    most = df.groupby("Parent-Cat")["Parent-Cat"].count().sort_values(ascending=False)
    most_list = list(most[:7].index)
    # Organize into Top 8 Categories
    for column in most_list:
        col = list(categories_df[column].dropna())
        df.loc[df["Category"].str.contains("|".join(col)), "Category2"] = column

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

        button_load = ttk.Button(self, text="Load", command=lambda: self.load(controller))
        button_load.grid(row=1, column=2)

        button_budget = ttk.Button(self, text="Budget", command=lambda: controller.show_frame(BudgetPage))
        button_budget.grid(row=2, column=1)

        self.load_text = tk.StringVar()
        label_load = tk.Label(self, textvariable=self.load_text)
        label_load.grid(row=3, column=1)

    def load(self, controller):
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
        duration = (tod - datetime.timedelta(days=(6 * 31))).strftime("%Y-%m")
        str_date = duration.split("-")

        # TODO: Make years more dynamic
        years = list(range(2005, tod.year + 1, 1))  # initial default
        # years = self.controller.dataframe.sort_index().index.strftime("%Y").astype("int")
        self.opt_month = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November',
                          'December']
        self.opt_year = list(range(years[0], years[-1] + 1, 1))

        # Set default selections for drop down menus
        self.em_var = tk.StringVar(self)
        self.em_var.set(tod.strftime("%B"))

        self.ey_var = tk.StringVar(self)
        self.ey_var.set(tod.year)

        self.sm_var = tk.StringVar(self)
        self.sm_var.set(self.opt_month[int(str_date[1])])

        self.sy_var = tk.StringVar(self)
        self.sy_var.set(str_date[0])

        # Create Dropdown menus for start and end date
        self.startmonth_dd = ttk.Combobox(self, textvariable=self.sm_var, values=self.opt_month,
                                          state="disabled", width=12)
        self.startyear_dd = ttk.Combobox(self, textvariable=self.sy_var, values=self.opt_year,
                                         state="disabled", width=12)
        self.endmonth_dd = ttk.Combobox(self, textvariable=self.em_var, values=self.opt_month,
                                        state="readonly", width=12)
        self.endyear_dd = ttk.Combobox(self, textvariable=self.ey_var, values=self.opt_year,
                                       state="readonly", width=12)
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
        self.cat_options = category_list
        self.cat_var = tk.StringVar(self)
        self.cat_var.set(self.cat_options[0])  # default value

        self.dropdown = ttk.Combobox(self, textvariable=self.cat_var, values=self.cat_options,
                                     state="disabled", width=12)
        self.dropdown.grid(row=3, column=2, columnspan=1)  # pack(side=tk.TOP) # side=tk.RIGHT

        # Dropdown for plot type
        self.plot_options = ["Monthly Breakdown", "Relative to Income", "Net Income", "Individual Category"]
        self.plt_var = tk.StringVar()
        self.plt_var.set(self.plot_options[0])
        self.plt_dd = ttk.Combobox(self, textvariable=self.plt_var, values=self.plot_options,
                                   state="readonly", width=17)
        self.plt_dd.grid(row=3, column=3)
        self.plt_dd.bind('<<ComboboxSelected>>', lambda event: self.on_select())

        # Button to plot category
        plot_button = ttk.Button(self, text="Plot",
                                 command=lambda: self.plot_data(self.canvas))
        plot_button.grid(row=3, column=4)  # pack()

        # Canvas to plot on
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=16, rowspan=20, padx=10,
                                         pady=10)  # pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)  # fill=tk.BOTH, , expand=True

        # Button to calculate budget
        budget_button = ttk.Button(self, text="Calculate Budget",
                                   command=self.budget_cal)
        budget_button.grid(row=2, column=20, columnspan=2)  # pack()

        r = 4
        for cat5 in self.controller.budget_dict.keys():
            tk.Label(self, text=cat5).grid(row=r, column=21)
            tk.Entry(self, textvariable=self.controller.budget_dict[cat5]).grid(row=r, column=22)
            r += 1

        # Top 5 Categories
        self.top5 = tk.StringVar(value=" ")
        self.t5_label = tk.Label(self, text=self.top5)
        self.t5_label.grid(row=2, column=24)

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
            chk = tk.Checkbutton(top, text=acct.title(), variable=self.controller.account_dict[acct], onvalue=1,
                                 offvalue=0,
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

        okaybutton = ttk.Button(top, text="Okay", command=lambda: okayfun(self, top=top))  # lambda: okayfun(top)
        okaybutton.grid(row=row + 3, column=3, padx=5, pady=5, sticky="W")

        def okayfun(self, top):
            cont = self.controller
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

            # Update OptionMenu for Categories
            categories_on = [key.lower() for (key, value) in cont.category_dict.items() if value.get() == 1]
            update_option_menu(self.dropdown, categories_on, self.cat_var)
            # menu = self.dropdown["menu"]
            # menu.delete(0, "end")
            # categories_on = [key.lower() for (key, value) in cont.category_dict.items() if value.get() == 1]
            # for string in categories_on:
            #     menu.add_command(label=string.title(),
            #                      command=lambda value=string.title(): self.ddvar.set(value))

            # Close pop up window
            top.destroy()

    def plot_data(self, canvas):
        # Clear Figure
        f.clear()
        # a1 = f.add_subplot(211)
        # a2 = f.add_subplot(212)

        # Get filter settings
        account_dict = self.controller.account_dict
        category_dict = self.controller.category_dict
        accounts_on = [key for (key, value) in account_dict.items() if value.get() == 1]
        categories_on = [key.lower() for (key, value) in category_dict.items() if value.get() == 1]

        # Setup Dataframe
        df = self.controller.dataframe.copy()

        # Apply Filters
        df = df[(df['Account Name'].str.contains("|".join(accounts_on))) &
                (df['Category2'].str.contains("|".join(categories_on)))]

        option_selected = self.plt_dd.get()

        if (option_selected == self.plot_options[0]) | (option_selected == self.plot_options[1]):
            # Create axis for plot
            a = f.add_subplot(111)
            pie_colors = cb.Paired_8.hex_colors  # Colors to be used by pie chart

            # Month Selected Filtering
            end_date, start_date = self.get_dates()[:2]
            # Filter Data between start and end dates
            df = df[(df.index >= start_date) & (df.index <= end_date)]

            # Get Total Expenses
            temp2_df = df[(df['Category2'] != "income") & (df['Transaction Type'] == "debit")]
            totExp_avg = temp2_df.groupby(pd.Grouper(freq="M"))["Amount"].sum().mean()
            totIncome = df.loc[df['Category2'] == "income", "Amount"].sum()
            temp2 = temp2_df.groupby([pd.Grouper(freq="M"), "Category2"])["Amount"].sum()
            end_month = end_date.strftime("%B")
            plt_title = "Total Expenses for " + end_month + ": $" + format(round(totExp_avg, 2), "6,.2f")

            if option_selected == self.plot_options[1]:
                plt_title = "Monthly Expenses Relative \n to Total Income: $" + format(round(totIncome, 2), "6,.2f")
                pie_colors = cb.Accent_8.hex_colors

            # Consolidate categories less than 5% together
            prct = (temp2/totExp_avg)*100
            misc_list = []
            if prct[prct < 5].count() > 1:  # If more than 1 cat is less than 5% combine
                other = 0
                new_index = ""
                data2plot = pd.Series()
                for ind1, ind2 in temp2.index:
                    if prct.loc[(ind1, ind2)] < 5:
                        other += temp2.loc[(ind1, ind2)]
                        new_index = "misc"
                        misc_list.append(ind2.title() + ": " + str(round(prct.loc[(ind1, ind2)], 2)) + "%")
                    else:
                        data2plot.loc[ind2] = temp2.loc[(ind1, ind2)]

                data2plot.loc[new_index] = other
            else:
                temp2 = temp2.reset_index(level='Category2')
                data2plot = temp2.groupby("Category2")["Amount"].mean().sort_values(ascending=False)




            # Plot Pie Chart
            # pie_explode = tuple([0.05]*len(data2plot.index))
            pie_labels = [x.title() for x in data2plot.index]
            pie_props = {"edgecolor": "w", 'linewidth': 1.5, 'linestyle': '-', 'antialiased': True}
            a.pie(data2plot, startangle=45, wedgeprops=pie_props, colors=pie_colors, labels=pie_labels,
                  autopct=lambda pct: self.pct_func(pct, data2plot, totExp_avg, totIncome, option_selected),
                  pctdistance=0.65, textprops={'fontsize': 10})

            a.set_title(plt_title)
            if misc_list:
                misc_str = "\n".join(misc_list)
                props = dict(boxstyle='round', facecolor='grey', alpha=0.5)
                # place a text box in upper left in axes coords
                a.text(0.0, 0.0, misc_str, transform=a.transAxes, fontsize=8,
                        verticalalignment='bottom', bbox=props)

        # ## Plot: Net Income
        elif option_selected == self.plot_options[2]:
            # Create axes
            a1 = f.add_subplot(211)
            a2 = f.add_subplot(212, sharex=a1)

            # Get duration from entry or dropdown
            end_date, start_date = self.get_dates(start=True)[:2]
            # Filter Data between start and end date
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            # Create new DataFrame for data to plot
            data2plot = pd.DataFrame()
            data2plot["monthly_income"] = df[df["Category2"] == "income"].groupby(pd.Grouper(freq="M"))["Amount"].sum()
            data2plot["monthly_expense"] = df[(df["Category2"] != "income") & (df['Transaction Type'] == "debit")].groupby(
                pd.Grouper(freq="M"))["Amount"].sum()
            data2plot["monthly_net"] = data2plot["monthly_income"]-data2plot["monthly_expense"]
            # Format index
            data2plot.index = data2plot.index.strftime("%b %y")

            # Pre-plot Settings
            bar_width = 0.3
            x_labels = data2plot.index
            x1 = np.arange(len(data2plot.index)) - bar_width/2
            x2 = [x + bar_width for x in x1]

            colors = {"light-green": (0.2, 0.8, 0.3, 0.6), "dark-green": (0.1, 0.9, 0.2, 0),
                      "light-red": (0.8, 0.3, 0.2, 0.6), "dark-red": (0.9, 0.2, 0.1, 0),
                      "light-blue": (0.2, 0.3, 0.8, 0.6), "dark-blue": (0.1, 0.2, 0.9, 0)}


            # Plot Income vs Expenses
            a1.bar(x=x1, height=data2plot["monthly_income"], width=bar_width, color=colors["light-green"],
                   edgecolor=colors["dark-green"], label="Income", align="center")  # plots income bars
            a1.bar(x=x2, height=data2plot["monthly_expense"], width=bar_width, color=colors["light-red"],
                   edgecolor=colors["dark-red"], label="Expense", align="center")  # plots expense bars

            # a1.autoscale(tight=True)  # suppose to fit everything inside figure
            a1.grid(axis="y", color="black", alpha=.5, linewidth=.5)
            a1.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('${x:,.0f}'))
            a1.tick_params(axis='both', which='major', labelsize=8)
            a1.label_outer()  # hides x-tick labels
            a1.set_ymargin(0.3)  # adds margin to y limits
            a1.legend(fontsize=8)  # adds legend
            a1.set_title("Income vs Expense", fontsize=10)


            # Plot Net Income
            a2.bar(x=x1, height=data2plot["monthly_net"], width=bar_width, color=colors["light-blue"],
                   edgecolor=colors["dark-blue"], tick_label=x_labels, label="Net Income", align="center")  # plots net income bars

            # a2.autoscale(tight=True)
            a2.set_ymargin(0.3)  # adds margin to y limits
            a2.set_ylim(a2.get_ylim()[0], a1.get_ylim()[1])  # keeps original ymin limit, uses ymax limit from a1 axes
            a2.set_title("Net Income", fontsize=10)
            a2.tick_params(axis='both', which='major', labelsize=8)
            a2.set_xticklabels(labels=a2.get_xticklabels(), rotation=45)   # rotates labels 45 degrees
            a2.grid(axis="y", color="black", alpha=.5, linewidth=.5)  # adds y-grids to plot
            a2.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('${x:,.0f}'))  # formats y ticks to $#,###


        # Plot Individual Category
        else:
            # Create axes
            a1 = f.add_subplot(211)
            a2 = f.add_subplot(212)

            # Get selected category from dropdown
            end_date, start_date, selected_cat = self.get_dates(start=True)
            # Filter Data between start and end dates
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            # Narrow down to selected Category
            df = df[df['Category2'] == str(selected_cat).lower()]
            # Groupby
            data2plot1 = df.groupby(pd.Grouper(freq='M'))['Amount']. \
                agg(['mean', 'sum', 'max']).sort_values(by=['Date', 'sum'], ascending=[True, False])

            # Set Date format for x-axis ticks
            data2plot1.index = data2plot1.index.strftime("%b %y")

            # Pre-plot Settings
            bar_width = 0.3
            x_labels = data2plot1.index
            x1 = np.arange(len(data2plot1.index)) - bar_width / 2  # sum
            x2 = [x + bar_width for x in x1]  # max
            x3 = [x - bar_width for x in x1]  # mean

            colors = {"light-green": (0.2, 0.8, 0.3, 0.6), "dark-green": (0.1, 0.9, 0.2, 0),
                      "light-red": (0.8, 0.3, 0.2, 0.6), "dark-red": (0.9, 0.2, 0.1, 0),
                      "light-blue": (0.2, 0.3, 0.8, 0.6), "dark-blue": (0.1, 0.2, 0.9, 0)}

            pie_colors = cb.Dark2_8.hex_colors

            # Plot data
            try:
                # Plot bars
                a1.bar(x=x1, height=data2plot1["sum"], width=bar_width, color=colors["light-red"],
                       edgecolor=colors["dark-red"], label="Sum", align="center")  # plots sum bars
                a1.bar(x=x2, height=data2plot1["max"], width=bar_width, color=colors["light-blue"],
                       edgecolor=colors["dark-blue"], label="Max", align="center")  # plots max bars
                a1.bar(x=x3, height=data2plot1["mean"], width=bar_width, color=colors["light-green"],
                       edgecolor=colors["dark-green"], label="Mean", align="center", tick_label=x_labels)  # plots mean bars
                # data2plot1.plot(kind='bar', ax=a1, rot=70)

                # Plot Average line
                a1.axhline(y=data2plot1['sum'].mean(), linestyle='--', color='r', label='Avg Sum')

                # Set rest of plot settings
                a1.legend(fontsize=8)
                a1.set_xticklabels(labels=a1.get_xticklabels(), rotation=45)
                a1.set_ylabel('Cost ($)')
                a1.set_ymargin(0.3)
                a1.tick_params(axis='both', which='major', labelsize=8)
                a1.set_title(selected_cat)
                a1.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('${x:,.0f}'))
            except TypeError as e:
                a1.text(0.35, 0.5, e, dict(size=25), wrap=True)
                a1.axis("Off")

            data2plot2 = df.groupby("Category")['Amount'].sum().sort_values(ascending=False)

            # Plot pie
            a2.pie(data2plot2, labels=list(data2plot2.index), colors=pie_colors, autopct='%1.1f%%',
                   textprops={'fontsize': 8})

        plt.tight_layout()
        canvas.draw()

    def budget_cal(self):

        # Create copy of dataframe to use
        df = self.controller.dataframe.copy()
        option_selected = self.plt_dd.get()
        if (option_selected == self.plot_options[0]) | (option_selected == self.plot_options[1]):
            end_date, start_date = self.get_dates()[:2]
        else:
            end_date, start_date = self.get_dates(start=True)[:2]
        # Filter data between start and end dates
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        # TODO: Switch Calculation if only looking at a month or over a few months
        # Calculate Average Income
        income = df.loc[df['Category2'] == "income", "Amount"].copy()
        expense = df[(df['Category2'] != "income") & (df['Transaction Type'] == "debit")].copy()
        # When only looking at only one month
        if end_date.strftime("%B") == start_date.strftime("%B"):
            avg_income = income.sum()  # Total Income for the month
            avg_expense = expense["Amount"].sum()  # # Total Expenses for the month
        # When looking over several months
        else:
            avg_income = income.groupby(pd.Grouper(freq="M"))["Amount"].sum().mean()  # Average of total monthly income
            avg_expense = expense.groupby(pd.Grouper(freq="M"))["Amount"].sum().mean()  # Average of total monthly expenses
        # TODO: finish calculating budget based on income, 50/30/20, etc
        # Create 50/30/20 categories:
        # 50%: Bills, Food ; 30%: Fun, Shopping, Travel, Misc, Other; 20%: Savings
        bgt_503020 = [1.25, 1.25, 1.15, 1.15, 1.15, 1.15]
        # Calculate Weights for each category
        weights = expense.groupby([pd.Grouper(freq="M"), "Category2"])["Amount"].sum()
        weights = weights/avg_expense
        budget = weights*income*bgt_503020





        # tod = datetime.datetime.today()  # today
        # duration = (tod - datetime.timedelta(days=(6 * 31))).strftime("%Y-%m")
        # df = self.controller.dataframe.copy()
        # df = df[df.index > duration]
        #
        # # Caclulate averages
        # income = df[(df['Category2'] == "income")].groupby(
        #     pd.Grouper(freq='M'))['Amount'].max().mean()
        # avg_list = ['bills', 'food', 'travel', 'shopping', 'fun', 'misc', 'other']
        # averages = []
        #
        # for item in avg_list:
        #     b = df[(df['Category2'] == item)].groupby(
        #         pd.Grouper(freq='M'))['Amount'].sum().mean()
        #     b *= 1.03  # add 3% margin
        #     averages.append(b)
        #
        # savings = income - sum(averages)
        #
        # budget_list = [income] + averages + [savings]
        #
        # r = 0
        # for key in self.controller.budget_dict.keys():
        #     self.controller.budget_dict[key].set(value=round(budget_list[r], ndigits=2))
        #     r += 1
        #
        # # Update top 5 Categories

        # self.top5.set("Top 5 Categories")
        # top5 = df.groupby("Category2")["Amount"].agg({"Total": "sum"}).sort_values(by="Total", ascending=False)
        # income = float(top5.loc["income"])
        # top5["percent"] = (top5["Total"] / income) * 100
        # top5.drop(labels="income", axis=0, inplace=True)
        # top5_list = list(top5.index)
        # for i in range(len(top5)):
        #     tk.Label(self, text=top5_list[i]).grid(r)

    def on_select(self, event=None):
        # Settings for Monthly Breakdown
        if (self.plt_dd.get() == self.plot_options[0]) | (self.plt_dd.get() == self.plot_options[1]):
            self.dropdown["state"] = "disabled"
            self.startmonth_dd["state"] = "disabled"
            self.startyear_dd["state"] = "disabled"
            self.endmonth_dd["state"] = "readonly"
            self.endyear_dd["state"] = "readonly"

        elif self.plt_dd.get() == self.plot_options[2]:
            self.dropdown["state"] = "disabled"
            self.startmonth_dd["state"] = "readonly"
            self.startyear_dd["state"] = "readonly"
            self.endmonth_dd["state"] = "readonly"
            self.endyear_dd["state"] = "readonly"
        else:
            self.dropdown["state"] = "readonly"
            self.startmonth_dd["state"] = "readonly"
            self.startyear_dd["state"] = "readonly"
            self.endmonth_dd["state"] = "readonly"
            self.endyear_dd["state"] = "readonly"
            self.dropdown["state"] = "readonly"
        pass

    def pct_func(self, pct, data, exp, inc, opt):
        actual = (pct / 100) * exp
        if opt == self.plot_options[0]:
            percent = pct
        elif opt == self.plot_options[1]:
            percent = (pct*exp)/inc  # same as (((pct/100)*exp)/inc)*100
        else:
            percent = None
        return "{:.1f}%\n(${:,.2f})".format(percent, actual)

    def get_dates(self, end=True, start=False):
        # Get end date
        end_month = self.em_var.get()
        end_year = self.ey_var.get()
        end_day = str(calendar.monthrange(int(end_year),
                                          int(datetime.datetime.strptime(end_month, "%B").strftime("%m")))[1])
        end_str = end_month + " " + end_day + " " + end_year
        end_date = datetime.datetime.strptime(end_str, '%B %d %Y')

        if start:
            # Get start date
            start_month = self.sm_var.get()
            start_year = self.sy_var.get()
            start_str = start_month + " " + start_year
            start_date = datetime.datetime.strptime(start_str, '%B %Y')
        else:
            start_str = end_month + " " + "01" + " " + end_year
            start_date = datetime.datetime.strptime(start_str, '%B %d %Y')

        # Get selected category from dropdown
        selected_cat = self.cat_var.get()

        return end_date, start_date, selected_cat


app = Budgetapp()
app.mainloop()
