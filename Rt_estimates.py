#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


# Youyang wu data

# In[70]:


yy_url = 'https://raw.githubusercontent.com/youyanggu/covid19_projections/master/r_values/latest_r_values_us.csv'
yy_rt = pd.read_csv(yy_url, parse_dates=['cur_date', 'inflection_date'])


# In[71]:


yy_rt.info()


# In[72]:


yy_rt = yy_rt[yy_rt['region'] != 'USA'].rename(columns={'region':'state', 'current_r':'yy_r'}).set_index('state')
yy_rt


# Lin lab data

# In[73]:


lin_url = 'https://github.com/lin-lab/COVID19-Viz/raw/master/clean_data/rt_table_export.csv'
lin_rt = pd.read_csv(lin_url, parse_dates=['date', 'date_lag'])


# In[74]:


lin_rt.columns


# In[75]:


lin_rt.info()


# In[77]:


lin_rt = lin_rt[lin_rt['resolution'] == 'state_USA']


# In[78]:



def get_state(state_str):
    return state_str.strip().split(',')[0]


# In[79]:


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


# In[80]:


lin_rt['state'] = lin_rt.dispID.apply(get_state).map(us_state_abbrev)


# In[81]:


lin_rt.head()


# In[82]:


lin_rt = lin_rt.set_index(['state', 'date']).sort_index()
lin_rt = lin_rt.groupby(level='state').tail(1).reset_index(level=1, drop=True)
lin_rt.rename(columns={'Rt_plot':'lin_r'}, inplace=True)


# In[87]:


lin_rt.head()


# In[97]:


kstv_url = 'https://d14wlfuexuxgcm.cloudfront.net/covid/rt.csv'
kstv_rt = pd.read_csv(kstv_url, parse_dates=['date']).rename(columns={'region':'state', 'mean':'kstv_r'})


# In[98]:


kstv_rt.columns


# In[99]:


kstv_rt = kstv_rt.set_index(['state', 'date']).sort_index()
kstv_rt = kstv_rt.groupby(level='state').tail(1).reset_index(level=1, drop=True)
kstv_rt.head()



# In[106]:


all_rt = lin_rt.join(yy_rt).join(kstv_rt, rsuffix='_x')[['lin_r', 'yy_r', 'kstv_r']].dropna()
all_rt[all_rt < 0] = 1.0
all_rt['mean'] = all_rt.mean(axis=1)


# In[107]:


all_rt.reset_index(inplace=True)
