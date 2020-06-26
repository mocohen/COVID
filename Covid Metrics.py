#!/usr/bin/env python
# coding: utf-8

# In[94]:


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
from matplotlib.dates import DateFormatter

import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from scipy.signal import savgol_filter

try:
    get_ipython().run_line_magic('matplotlib', 'inline')
    get_ipython().system(" curl -o states-daily.csv 'https://covidtracking.com/api/v1/states/daily.csv'")
except:
    print('Not in python notebook, images saved to file')
sns.set()


# In[95]:


#Read in covid cases csv
corona = pd.read_csv('states-daily.csv', index_col=[1,0], parse_dates=[0])
corona.head()


# In[96]:


us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


# In[97]:


# Read in state populations from census
state_populations = pd.read_csv('nst-est2019-01.csv', index_col=0, thousands=',')
state_populations.index = state_populations.index.map(us_state_abbrev)
state_populations.head()


# In[98]:


# join state populations to covid data
corona = corona.join(state_populations, on='state')


# In[99]:


corona.head()


# In[100]:


# sort on state
corona.sort_index(inplace=True)
# add percent of cases that are negative
corona['percentNegative'] = 100.0* corona['negativeIncrease'] / corona['totalTestResultsIncrease']


# In[101]:


columns_to_plot = ['positiveIncrease', 'totalTestResultsIncrease', 'percentNegative']
titles = ['# Positive', '# Tests', '% Negative']


# In[102]:


# is this increasing over the time span?
def isIncreasing(x):
    if x[0] < x[-1]:
        return True
    else:
        return False


# In[103]:


# add columns for rolling average, and if it is increasing
for col in columns_to_plot:
    new_col_name = col+'Rolling'
    corona[new_col_name] = corona.groupby(level=0)[col].rolling(window=7).mean().values
    
    comparison_name = col+'IsIncreasing'
    corona[comparison_name] = corona.groupby(level=0)[new_col_name].rolling(window=7).apply(isIncreasing, raw=True).values
        


# In[104]:


corona['positiveIncreaseRollingPer100k'] = 1e5*corona['positiveIncreaseRolling']/corona['population']


# In[105]:


# create plots for each metric
def plot_bar_increasing (ts, title, isIncreasing, ax, increaseGreen=True, population=None):
    if increaseGreen:
        mapping = {True: 'g', False: 'r'}
    else:
        mapping = {False: 'g', True: 'r'}
        
    if population is not None:
        ts = 1e5*ts / population
    
    ts.plot(kind='bar',
           color = isIncreasing.map(mapping),
           ax=ax)
    ax.set_ylabel(title)


# In[106]:


#plot 3 metrics
plt.rcParams.update({'font.size': 14})


# get most recent value for each state
corona_to_plot = corona.groupby(level='state').tail(1).reset_index(level=1, drop=True)

#create plot
fig, axs = plt.subplots(len(columns_to_plot), 1, sharex=True, figsize=(20,8))

# fill na with zeros
corona_to_plot.fillna(0.0, axis=1, inplace=True)

columns_to_plot = ['positiveIncrease', 'totalTestResultsIncrease', 'percentNegative']
titles = ['# Positive', '# Tests', '% Negative']

plt.suptitle('7-day Rolling Average for States\nGreen Improving. Red Worsening')

# plot positive cases
plot_bar_increasing(corona_to_plot['positiveIncrease'+'Rolling'], 
                    '# Positive / 100k', 
                    corona_to_plot['positiveIncrease'+'IsIncreasing'],
                    ax=axs[0],
                    increaseGreen=False,
                    population=corona_to_plot['population'])


#plot tests run
plot_bar_increasing(corona_to_plot['totalTestResultsIncrease'+'Rolling'], 
                    '# Tests / 100k', 
                    corona_to_plot['totalTestResultsIncrease'+'IsIncreasing'],
                    ax=axs[1],
                    increaseGreen=True,
                    population=corona_to_plot['population'])

#plot pct negative tests
plot_bar_increasing(corona_to_plot['percentNegative'+'Rolling'], 
                    '% Negative', 
                    corona_to_plot['percentNegative'+'IsIncreasing'],
                    ax=axs[2],
                    increaseGreen=True)


plt.savefig('images/state_by_state.pdf')
plt.savefig('images/state_by_state.svg')


# In[107]:


# is each metric improving or declining 

pos_mapping = {True: 1, False: -1}
neg_mapping = {False: 1, True: -1}

def isIncreasingZeroCheck(pct_neg, pct_neg_incr):
    if pct_neg < 1:
        return 0
    if pct_neg_incr > 0:
        return 1
    else:
        return -1

rate_mappings = []
rate_mappings.append(corona_to_plot['positiveIncrease'+'IsIncreasing'].map(neg_mapping))
rate_mappings.append(corona_to_plot['totalTestResultsIncrease'+'IsIncreasing'].map(pos_mapping))
rate_mappings.append(corona_to_plot.apply(lambda row: isIncreasingZeroCheck(row['percentNegative'], row['percentNegative'+'IsIncreasing']), axis=1)
)


# In[108]:


# are the metrics at good levels?
level_mappings = []
level_mappings.append((1e5*corona_to_plot['positiveIncreaseRolling']/corona_to_plot['population']).apply(lambda x: 1 if x < 5.0 else -1))
level_mappings.append(corona_to_plot['percentNegativeRolling'].apply(lambda x: -0.5 if x < 1 else (1 if x > 95 else -1)))


# In[109]:


fig, axs = plt.subplots(2, 1, figsize=(20,5))


#rates summary
im = axs[0].imshow(rate_mappings, cmap='RdYlGn', vmin=-1.25, vmax=1.25)
axs[0].set_title('Are these measures getting better or worse?')
# We want to show all ticks...
axs[0].set_xticks(np.arange(len(corona_to_plot.index)))
axs[0].set_yticks(np.arange(3))
# ... and label them with the respective list entries
axs[0].set_xticklabels(corona_to_plot.index.values)
axs[0].set_yticklabels(titles)
axs[0].set_ylim(-0.5,2.5)
axs[0].grid(False)
plt.setp(axs[0].xaxis.get_majorticklabels(), rotation=90)

#level summary
im = axs[1].imshow(level_mappings, cmap='RdYlGn', vmin=-1.25, vmax=1.25)
axs[1].set_title('Are these measures at reasonable levels in the community?')
# We want to show all ticks...
axs[1].set_xticks(np.arange(len(corona_to_plot.index)))
axs[1].set_yticks(np.arange(2))
# ... and label them with the respective list entries
axs[1].set_xticklabels(corona_to_plot.index.values)
axs[1].set_yticklabels(['L.T. 5 cases/100k', '20 Tests per pos. case'])
axs[1].set_ylim(-0.5,1.5)
axs[1].grid(False)

plt.setp(axs[1].xaxis.get_majorticklabels(), rotation=90)

plt.tight_layout()
plt.savefig('images/state_by_state_summary.pdf')
plt.savefig('images/state_by_state_summary.svg')


# In[110]:


rate_changes = []
rate_changes.append(corona_to_plot['positiveIncrease'+'Rolling'].map(neg_mapping))
rate_changes.append(corona_to_plot['totalTestResultsIncrease'+'IsIncreasing'].map(pos_mapping))
rate_changes.append(corona_to_plot.apply(lambda row: isIncreasingZeroCheck(row['percentNegative'], row['percentNegative'+'IsIncreasing']), axis=1)
)


level_changes = []
level_changes.append((1e5*corona_to_plot['positiveIncreaseRolling']/corona_to_plot['population']).apply(lambda x: 1 if x < 10.0 else -1))
level_changes.append(corona_to_plot['percentNegativeRolling'].apply(lambda x: 0 if x < 1 else (1 if x > 90 else -1)))


# In[112]:


g = sns.relplot(x="date", y="positiveIncreaseRollingPer100k", 
                col='state', 
                data=corona.reset_index(),
               kind="line", 
               col_wrap=8,
               height=1.5, aspect=1.2)
g.fig.autofmt_xdate()
g.set_xticklabels(rotation=45)
date_form = DateFormatter("%b")
g.axes[0,].xaxis.set_major_formatter(date_form)


g.set_ylabels('')
g.set_xlabels('')
g.set_titles('{col_name}')

g.fig.suptitle('Positive cases per 100k\n7-day Rolling Average', y=1.05, fontsize=16)
g.savefig('images/PositiveCases.svg')
g.savefig('images/PositiveCases.pdf')


# In[ ]:




