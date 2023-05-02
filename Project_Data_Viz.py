#!/usr/bin/env python
# coding: utf-8

# <h1> Fundamentals of Data Visualization Final Project </h1>
# 
# 

# In[ ]:





# In[458]:


# Import our data processing library (note: you may have to install this!)
import pandas as pd
import altair as alt
import geopandas as gpd
from altair import datum
from vega_datasets import data



# Uploading a dataset with teacher's salary by state for 1960-2021 merged with inflation adjusted living wage

data_sal= pd.read_csv("sal_cpi_live.csv")

#adjusted salary and convert date
#filter for year > = 2000
data_sal['adjusted']= round(data_sal['adjusted'],2)
data_sal['year']= data_sal['year'].astype(str)
#data_sal = data_sal[(data_sal['year'].str.contains("1960") == False)]
#data_sal = data_sal[(data_sal['year'].str.contains("1970") == False)]
#data_sal = data_sal[(data_sal['year'].str.contains("1980") == False)]
#data_sal = data_sal[(data_sal['year'].str.contains("1990") == False)]

#filter out Averages and only for 2021
data_2021 = data_sal[(data_sal['State'].str.contains("Average") == False)]
data_2021 = data_2021[(data_2021['State'].str.contains("Public") == False)]
data_2021 = data_2021[data_2021['year'] == "2021"]

selection = alt.selection(type='multi', fields=['State'])

bottom = alt.Chart(data_2021).mark_bar().encode(
    alt.X('State:N', axis=alt.Axis(title="State")),
    alt.Y('salary:Q', axis=alt.Axis(title="Salary ($)")),
    color=alt.condition(selection, alt.value('steelblue'), alt.value('lightblue')),
    tooltip=["State", "salary"]
).properties(
    width=600, height=200,
    title = 'Salary and Living Wage by State for 2021'
).add_selection(selection)

bubble = alt.Chart(data_2021).mark_circle(color = 'red').encode(
    x="State", 
    y="adjusted",
    tooltip=["State", "adjusted"]
    
)

top = alt.Chart(data_sal).mark_line(point=True).encode(
    alt.X('year:N', axis=alt.Axis(title="Year")),
    alt.Y('salary:Q', axis=alt.Axis(title="Salary ($)")),    
    tooltip=["State", "salary", "year"]    
).properties(
    width=600, height=200
).transform_filter(
    selection
)

top_adj = alt.Chart(data_sal).mark_line(point=True, color = 'red').transform_fold(
    fold=['salary', 'living wage'], 
    as_=['key', 'value']
).encode(
    x='year',
    y='adjusted',
    color=alt.Color('key:N', scale=alt.Scale(range=['red','steelblue'])),
    tooltip=["State", "adjusted", "year"]
).properties(
    width=600, height=200,
    title = 'Salary and Living Wage by Year'
).transform_filter(
    selection
)

alt.vconcat(
    top+top_adj, bottom+bubble
)
           
 


# In[ ]:





# In[518]:


data_sal['difference'] = round(data_sal['salary']- data_sal['adjusted'],2)
data_sal['percent_above'] = round((data_sal['salary']/data_sal['adjusted'])*100-100,2)
diff_df = data_sal[(data_sal['State'].str.contains("Average") == False)]
diff_df = diff_df[(diff_df['State'].str.contains("Public") == False)]

option_ar = ["","2021","2020","2019","2018","2017", "2016", "2015", "2014", "2013", "2012", "2011","2010","2009","2008","2007", "2006", "2005", "2004", "2003", "2000", "1990","1980", "1970"]

dropdown = alt.binding_select (options=option_ar, name="Select a year:")

selection = alt.selection(
    type="single",
    fields=['year'],
    bind=dropdown,
)

comp = alt.Chart(diff_df).mark_bar().encode(
    alt.X('percent_above:Q', axis=alt.Axis(title="Percent (%)")),
    tooltip=["State", "percent_above"],
    y = alt.Y(field='State', sort=alt.EncodingSortField('percent_above')),    
).properties(
    width=300, height=600,
    title='Comparison of Percentage above Living Wage by State'
).add_selection(
    selection
).transform_filter(
    selection
    
)


from IPython.display import HTML
display(HTML("""
<style>
form.vega-bindings {
  position: absolute;
  left: 500px;
  top: -4px;
}
</style>
"""))

display(comp)

comp.save('sal_map.html', embed_options={'renderer':'svg'})


# In[519]:


#state id info for mapping
from vega_datasets import data
pop = data.population_engineers_hurricanes()
pop.head()

states = alt.topo_feature(data.us_10m.url, 'states')
state_id = pop[['state', 'id']].copy()

click = alt.selection_multi(fields=['State'])

#filter out Averages and only for 2021
data_diff_2021 = diff_df[(diff_df['State'].str.contains("Average") == False)]
data_diff_2021 = data_diff_2021[(data_diff_2021['State'].str.contains("Public") == False)]
data_diff_2021 = data_diff_2021[data_diff_2021['year'] == "2021"]
#merge with state id's
newdf_diff = data_diff_2021.merge(state_id, left_on = 'State', right_on='state') 

#US chloropleth map with 2021 percentage above living wage
variable_list = ['salary', 'percent_above']


diff_map = alt.Chart(states).mark_geoshape().encode(
    tooltip=['State:N', 'percent_above:Q'],
    opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
    color=alt.Color('percent_above:Q')
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(newdf_diff, 'id', ['State', 'percent_above'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300,
    title='Percent Above Living Wage by State'
).add_selection(click)


# In[520]:


#filter out Averages and only for 2021
data_2021 = data_sal[(data_sal['State'].str.contains("Average") == False)]
data_2021 = data_2021[(data_2021['State'].str.contains("Public") == False)]
data_2021 = data_2021[data_2021['year'] == "2021"]
#merge with state id's
newdf = data_2021.merge(state_id, left_on = 'State', right_on='state') 

click = alt.selection_multi(fields=['State'])


sal_map = alt.Chart(states).mark_geoshape().encode(
    tooltip=['State:N', 'salary:Q'],
    opacity=alt.condition(click, alt.value(1), alt.value(0.2)),
    color='salary:Q'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(newdf, 'id', ['State', 'salary'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300,
    title = "Teacher Salary by State"
).add_selection(click)

sal_map
sal_map.save('sal_map.html', embed_options={'renderer':'svg'})


# In[521]:


diff_map
diff_map.save('diff_map.html', embed_options={'renderer':'svg'})


# In[522]:


selection = alt.selection(type='multi', fields=['State'], bind='legend')

c1 = alt.Chart(diff_df).mark_line().encode(
    alt.X('year:N', axis=alt.Axis(title="Year")),
    alt.Y('percent_above:Q', axis=alt.Axis(title="Percent (%)")),
    tooltip=["State", "percent_above", "year"],
    color=alt.Color('State', scale=alt.Scale(scheme='category20b'), legend=alt.Legend(columns=3,symbolLimit=0)),
    opacity=alt.condition(selection,alt.value(1),alt.value(.2))
).properties(
    width=500,
    height=500,
    title = "Historic Trends Percent Above Living Wage by State"
).add_selection(selection).interactive()

c1


# In[517]:


c1.save('webchart.html', embed_options={'renderer':'svg'})


# In[ ]:




