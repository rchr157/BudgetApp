# BudgetApp
App built with tkinter for viewing transaction data from Mint. Data is summarized into your top 7 categories and remaining categories are grouped into the "Other" category.

### Expected format
Date | Description | Original Descrition | Amount | Transaction Type | Category | Account Name | Labels | Notes 
---- | ----------- | ------------------- | ------ | ---------------- | -------- | ------------ | ------ | -----
03/21/2020 | Netflix | NETFLIX.COM | 8.99| debit | Movies & DVDs | Credit Card 1| | Example 


## How to Use:
### Step 1:
Load Mint excel/csv file. 
![Image of Load Screen](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot1-load.JPG)
![Image of Load Screen](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot2-main.JPG)

### Step2:
Select type of plot and date. Plot options include:
- Monthly Breakdown: Pie Chart Overview of Total Expenses for the month  
- Relative to Income: Pie Chart Overview of Expenses for the month relative to Income for that month
- Net Income: Bar Chart showing Income vs Expenses and overall net income for date specified
- Individual Category: Pie Chart showing makeup of category selected.

### Monthly Breakdown
Total expense for the month selected is shown in the title.
Percent and actual total for each category is shown in pie chart.
Categories less than 5% are grouped together and detailed on bottom left corner.
![Image of Monthly Breakdown](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot3a-monthlybreakdown.JPG)

### Relative to Income
Similar to Monthly breakdown except percentage is relative to Income for the month selected.
Total Income for selected month is shown in plot title.
![Image of Relative to Income](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot3b-rel2inc.JPG)

### Net Income
This plot option takes in an additional start date. 
Plots show Income vs Expenses along with the Net Income
![Image of Net Income](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot3c-netincome.JPG)

### Individual Category
Provides closer look at selected category over specified period.
Looks at monthly total, maximum, and average. Also provies the average total over the specified date.
![Image of Individual Category](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot3d-individualcat.JPG)

## Optional Features
### Calculate Budget
Calculate a preliminary budget for your top 7 Categories based on specified period. Remaining categories are grouped into "Other" category.
![Image of Calculate Budget](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot3e-calcbudget.JPG)

### Apply Filters
You can filter the data by 
- Account
- Category
- Price Range
![Image of Filter Settings](https://github.com/rchr157/BudgetApp/blob/master/screenshots/shot4-filter.JPG)
