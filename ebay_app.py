import streamlit as st
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import ssl
import urllib.request, urllib.parse

# GPUs, CPUs, and Motherboards I want to search
GPUs=['RTX 4090', 'RTX 4080', 'RX 7900 XTX', 'RTX 4070 Ti', 'RTX 3090 Ti',
      'RX 6950 XT', 'RX 7900 XT', 'RTX 3080 Ti', 'RTX 3090', 'RTX 3080',
      'RX 6900', 'RX 6800', 'RTX 3070', 'RTX 3070 Ti', 'RTX 2080 Ti',
      'RX 6800 XT', 'RX 6750 XT', 'RTX 3060 Ti', 'RX 6700 XT', 'RTX 2080 Super',
      'RTX 2080', 'GTX 1080 Ti', 'RTX 2070 Super', 'RX 6650 XT', 'RTX 3060',
      'RX 5700 XT', 'RTX 2060 Super', 'RX 6600 XT', 'RTX 2070', 'RTX 2060',
      'GTX 1080', 'RX 6600', 'RX 5700', 'GTX 1070 Ti', 'RTX 2060', 'GTX 980 Ti',
      'RX 5600 XT', 'GTX 1070', 'GTX 1660 Super', 'GTX 1660', 'GTX 3050',
      'GTX 1650 Super','GTX 1060','RX 6500 XT', 'GTX 760 Ti', 'GTX 750 Ti',
      'GTX 1050']
CPUs= ['AMD Ryzen 5 3600', 'AMD Ryzen 5 5500', 'AMD Ryzen 5 5600', 'AMD Ryzen 5 4600G',
       'AMD Ryzen 5 4500','AMD Ryzen 5 5600X','AMD Ryzen 9 3900X','AMD Ryzen 7 4700G', 'AMD Ryzen 7 3700X',
       'AMD Ryzen 7 2700X', 'AMD Ryzen 5 3600X', 'AMD Ryzen 7 4700', 'AMD Ryzen 7 5700','AMD Ryzen 7 5800X3D',
       'AMD Ryzen 5 5600X', 'AMD Ryzen 7 5800', 'AMD Ryzen 5 7600X', 'AMD Ryzen 5 7600','AMD Ryzen 7 5700X',
       'AMD Ryzen 9 5900', 'AMD Ryzen 9 3950X','AMD Ryzen 9 7950X','AMD Ryzen 9 7900X','AMD Ryzen 9 5900X',
       'AMD Ryzen 7 7700','AMD Ryzen 7 7700X','Intel Core i5-13500', 'Intel Core i5-6500','Intel Core i5-6600',
       'AMD Ryzen 9 7900',' Intel Core i9-13900K',' Intel Core i7-13700',' Intel Core i5-13600','Intel Core i7-13700F',
       'Intel Core i5-13400','Intel Core i7-9700K', 'Intel Core i7-9800X', 'Intel Core i7-14700KF',
       'Intel Core i9-12900K',' Intel Core i7-12700K','Intel Core i5-12600K','Intel Core i5-12400',
       'Intel Core i5-12500','Intel Core i7-13700K','Intel Core i7-10700','Intel Core i7-9700','Intel Core i5-10400','Intel Core i5-10500','Intel Core i5-10600','Intel Core i5-10600K'
       'Intel Core i9-11900K',' Intel Core i7-11700K','Intel Core i5-11600','Intel Core i5-11400F','Intel Core i5-11600K','Intel Core i5-11500',
       'Intel Core i7-7800X','Intel Core i7-6850K',' Intel Core i5-11400','Intel Core i5-14600K']
Motherboards= ['b450 motherboard', 'b550 motherboard', 'b460 motherboard', 'b560 motherboard', 'a520 motherboard','h470 motherboard',
               'h510 motherboard','h570 motherboard','z490 motherboard','z590 motherboard',
               'x570 motherboard','b650 motherboard','x670 motherboard','z790 motherboard', 'x470 motherboard','h410 motherboard',
               'B760 motherboard','z390 motherboard','h610 motherboard','b660 motherboard','x370 motherboard','b350 motherboard']

@st.cache_data
def cpu_scraper():
    # Links
    cpu_urlp1 = 'https://www.ebay.com/sch/i.html?_fsrp=1&rt=nc&_from=R40&_nkw='
    cpu_urlp2 = '&_sacat=0&LH_Sold=1&LH_Complete=1&LH_PrefLoc=1&_udlo=20&LH_ItemCondition=1500%7C3000%7C1000&_ipg=120'
    
    # Init 
    names = []
    prices = []
    dates = []
    shipping = []
    search_term = []
    i=1
    for cpu in CPUs:
        #bar1.progress((i/len(CPUs)))
        i = i+1
        searchstr=(cpu.replace(" ", "%20"))
        url=str.join("", [cpu_urlp1, searchstr, cpu_urlp2])
        html=urllib.request.urlopen(url).read()
        soup=BeautifulSoup(html,'html.parser')
        # Check for 'Results matching fewer words' and modify the soup
        soup_str = str(soup)
        cutoff_index = soup_str.find("Results matching fewer words")
        if cutoff_index != -1:
            truncated_html = soup_str[:cutoff_index]
            soup = BeautifulSoup(truncated_html, 'html.parser')
    
        main_data=soup.find_all('div',class_="s-item__info clearfix")

        # For each item get key data & add to a set of variables 
        for line in main_data:
            if "to" not in line.find("span",class_="s-item__price").get_text():
                if "Shop on eBay" not in line.find("a",class_="s-item__link").get_text():
                    names.append(line.select_one(".s-item__title span").text)
                    prices.append(line.find("span",class_="s-item__price").get_text())
                    dates.append(line.find("span",class_="POSITIVE").get_text())
                    search_term.append(cpu)
                    try:
                        shipping.append(line.find("span",class_='s-item__shipping s-item__logisticsCost').get_text())
                    except:
                        shipping.append('NA')
    prices = [price.replace("$", "") for price in prices]
    prices = [price.replace(",", "") for price in prices]
    dates = [date.replace("Sold ","") for date in dates]
    #prices = [float(price) for price in prices]
    df = pd.DataFrame({
    "search_term":search_term,
    "item_name": names,
    "price": prices,
    'shipping':shipping,
    'date_sold':dates
    })
    df = df[df["item_name"].str.contains("Combo") == False] 
    df = df[df["item_name"].str.contains("combo") == False]
    df = df[df["item_name"].str.contains("box") == False]  
    df = df[df["item_name"].str.contains("Box") == False] 
    df = df[df["item_name"].str.contains("BOX") == False]
    df = df[df["item_name"].str.contains("parts only") == False]  
    df = df[df["item_name"].str.contains("Fan") == False] 
    df = df[df["item_name"].str.contains("fan") == False] 
    df = df[df["item_name"].str.contains("Bracket") == False] 
    df = df[df["item_name"].str.contains("bracket") == False] 
    df = df[df["item_name"].str.contains("Replacement") == False] 
    df = df[df["item_name"].str.contains("empty") == False] 
    df = df[df["item_name"].str.contains("EMPTY") == False] 
    df = df[df["item_name"].str.contains("Empty") == False] 
    df = df[df["item_name"].str.contains("Read") == False] 
    df = df[df["item_name"].str.contains("READ") == False] 
    df = df[df["item_name"].str.contains("read") == False] 
    df = df[df["item_name"].str.contains("Damage") == False] 
    df = df[df["item_name"].str.contains("DAMAGE") == False] 
    df = df[df["item_name"].str.contains("Laptop") == False] 
    df = df[df["item_name"].str.contains("LAPTOP") == False]
    df['price'] = df['price'].apply(pd.to_numeric)
    return df
    
#-------
@st.cache_data
def gpu_scraper():
    # Links
    gpu_urlp1 = 'https://www.ebay.com/sch/i.html?_dcat=27386&_fsrp=1&rt=nc&_from=R40&_nkw='
    gpu_urlp2 = '&_sacat=0&LH_Sold=1&LH_Complete=1&LH_PrefLoc=1&LH_ItemCondition=1000%7C1500%7C2000%7C2010%7C2020%7C2030%7C3000&_ipg=240'
    # Init 
    names = []
    prices = []
    dates = []
    shipping = []
    search_term = []
    i = 1
    for gpu in GPUs:
        #bar2.progress((i/len(GPUs)))
        i = i+1
        searchstr=(gpu.replace(" ", "%20"))
        url=str.join("", [gpu_urlp1,searchstr,gpu_urlp2])
        html=urllib.request.urlopen(url).read()
        soup=BeautifulSoup(html,'html.parser')
        # Check for 'Results matching fewer words' and modify the soup
        soup_str = str(soup)
        cutoff_index = soup_str.find("Results matching fewer words")
        if cutoff_index != -1:
            truncated_html = soup_str[:cutoff_index]
            soup = BeautifulSoup(truncated_html, 'html.parser')
    
        main_data=soup.find_all('div',class_="s-item__info clearfix")

        # For each item get key data & add to a set of variables 
        for line in main_data:
            if "to" not in line.find("span",class_="s-item__price").get_text():
                if "Shop on eBay" not in line.find("a",class_="s-item__link").get_text():
                    names.append(line.select_one(".s-item__title span").text)
                    prices.append(line.find("span",class_="s-item__price").get_text())
                    dates.append(line.find("span",class_="POSITIVE").get_text())
                    search_term.append(gpu)
                    try:
                        shipping.append(line.find("span",class_='s-item__shipping s-item__logisticsCost').get_text())
                    except:
                        shipping.append('NA')
    prices = [price.replace("$", "") for price in prices]
    prices = [price.replace(",", "") for price in prices]
    dates = [date.replace("Sold ","") for date in dates]
    #prices = [float(price) for price in prices]
    df = pd.DataFrame({
    "search_term":search_term,
    "item_name": names,
    "price": prices,
    'shipping':shipping,
    'date_sold':dates
    })
    df = df[df["item_name"].str.contains("Combo") == False] 
    df = df[df["item_name"].str.contains("combo") == False]
    df = df[df["item_name"].str.contains("box") == False]  
    df = df[df["item_name"].str.contains("Box") == False] 
    df = df[df["item_name"].str.contains("BOX") == False]
    df = df[df["item_name"].str.contains("parts only") == False]  
    df = df[df["item_name"].str.contains("Fan") == False] 
    df = df[df["item_name"].str.contains("fan") == False] 
    df = df[df["item_name"].str.contains("Bracket") == False] 
    df = df[df["item_name"].str.contains("bracket") == False] 
    df = df[df["item_name"].str.contains("Replacement") == False] 
    df = df[df["item_name"].str.contains("empty") == False] 
    df = df[df["item_name"].str.contains("EMPTY") == False] 
    df = df[df["item_name"].str.contains("Empty") == False] 
    df = df[df["item_name"].str.contains("Read") == False] 
    df = df[df["item_name"].str.contains("READ") == False] 
    df = df[df["item_name"].str.contains("read") == False] 
    df = df[df["item_name"].str.contains("Damage") == False] 
    df = df[df["item_name"].str.contains("DAMAGE") == False] 
    df = df[df["item_name"].str.contains("Laptop") == False] 
    df = df[df["item_name"].str.contains("LAPTOP") == False] 
    df['price'] = df['price'].apply(pd.to_numeric)
    return df

@st.cache_data
def mboard_scraper():
  # Links
  mb_urlp1 = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
  mb_urlp2 = '&_sacat=0&LH_Sold=1&LH_Complete=1&LH_ItemCondition=1500%7C3000%7C2000&rt=nc&LH_PrefLoc=1'
  # Init 
  names = []
  prices = []
  dates = []
  shipping = []
  search_term = []
  i = 1
  for mb in Motherboards:  
    #bar3.progress((i/len(Motherboards)))
    i=i+1
    searchstr=(mb.replace(" ", "%20"))
    url=str.join("", [mb_urlp1,searchstr,mb_urlp2])
    html=urllib.request.urlopen(url).read()
    soup=BeautifulSoup(html,'html.parser')
    # Check for 'Results matching fewer words' and modify the soup
    soup_str = str(soup)
    cutoff_index = soup_str.find("Results matching fewer words")
    if cutoff_index != -1:
        truncated_html = soup_str[:cutoff_index]
        soup = BeautifulSoup(truncated_html, 'html.parser')
    
    main_data=soup.find_all('div',class_="s-item__info clearfix")

    # For each item get key data & add to a set of variables 
    for line in main_data:
      if "to" not in line.find("span",class_="s-item__price").get_text():
        if "Shop on eBay" not in line.find("a",class_="s-item__link").get_text():
          names.append(line.select_one(".s-item__title span").text)
          prices.append(line.find("span",class_="s-item__price").get_text())
          dates.append(line.find("span",class_="POSITIVE").get_text())
          search_term.append(mb)
          try:
            shipping.append(line.find("span",class_='s-item__shipping s-item__logisticsCost').get_text())
          except:
            shipping.append('NA')
  prices = [price.replace("$", "") for price in prices]
  prices = [price.replace(",", "") for price in prices]
  dates = [date.replace("Sold ","") for date in dates]
  #prices = [float(price) for price in prices]
  df = pd.DataFrame({
    "search_term":search_term,
    "item_name": names,
    "price": prices,
    'shipping':shipping,
    'date_sold':dates
  })
  df = df[df["item_name"].str.contains("Combo") == False] 
  df = df[df["item_name"].str.contains("combo") == False]
  df = df[df["item_name"].str.contains("box") == False]  
  df = df[df["item_name"].str.contains("Box") == False] 
  df = df[df["item_name"].str.contains("BOX") == False]
  df = df[df["item_name"].str.contains("parts only") == False]  
  df = df[df["item_name"].str.contains("Fan") == False] 
  df = df[df["item_name"].str.contains("fan") == False] 
  df = df[df["item_name"].str.contains("Bracket") == False] 
  df = df[df["item_name"].str.contains("bracket") == False] 
  df = df[df["item_name"].str.contains("Replacement") == False] 
  df = df[df["item_name"].str.contains("empty") == False] 
  df = df[df["item_name"].str.contains("EMPTY") == False] 
  df = df[df["item_name"].str.contains("Empty") == False] 
  df = df[df["item_name"].str.contains("Read") == False] 
  df = df[df["item_name"].str.contains("READ") == False] 
  df = df[df["item_name"].str.contains("read") == False] 
  df = df[df["item_name"].str.contains("Damage") == False] 
  df = df[df["item_name"].str.contains("DAMAGE") == False] 
  df = df[df["item_name"].str.contains("Laptop") == False] 
  df = df[df["item_name"].str.contains("LAPTOP") == False] 
  df['price'] = df['price'].apply(pd.to_numeric)
  return df

@st.cache_data
def cpu_marks():
  cpu_list = 'https://www.cpubenchmark.net/cpu_list.php'
  html=urllib.request.urlopen(cpu_list).read()
  soup=BeautifulSoup(html,'html.parser')

  # Init
  names = []
  marks = []
  table_data = soup.find_all('tbody')
  for line in table_data[0].find_all('tr'):
      #print(line('a')[0].get_text())
      names.append(line.find_all('td')[0].get_text()) # Name
      marks.append(line.find_all('td')[1].get_text()) # CPU Mark
      #print(line.find_all('td')[2].get_text()) # Rank
      #print(line.find_all('td')[3].get_text()) # Value
      #print(line.find_all('td')[4].get_text()) # Price

  marks = [mark.replace(',','') for mark in marks]
  df = pd.DataFrame({
    "cpu_name":names,
    "cpu_marks": marks,
  })
  df['cpu_marks'] = df['cpu_marks'].apply(pd.to_numeric)
  return df

@st.cache_data
def gpu_marks():
    gpu_list = 'https://www.videocardbenchmark.net/high_end_gpus.html'
    df = pd.DataFrame(columns=['gpu_name','scale','gpu_marks','price','blank'],index=range(10000))
    html=urllib.request.urlopen(gpu_list).read()
    soup=BeautifulSoup(html,'html.parser')
    i = 0
    j = 0 
    for line in (soup.find('span',class_='more_details').find_all_next('span')):
        if line.get_text() == 'Radeon Ryzen 5 5600GE':
            break
        else:
            #print(line.get_text(),i)
            df.iloc[j,i] = line.get_text()
            i = i + 1
            if i == 5:
                i = 0
                j = j+1

    df = df.drop(columns=['scale','price','blank'],axis='columns')
    df = df.dropna(how='all',axis= 'rows')
    #df['gpu_marks'] = df['gpu_marks'].apply(str.replace(',',''))
    #marks = [mark.replace(',','') for mark in marks]
    df['gpu_marks'] = [marks.replace(',','') for marks in df['gpu_marks']]
    
    df['gpu_marks'] = df['gpu_marks'].apply(pd.to_numeric)
    return df

st.title('Ebay Price Performance')
st.write("This application will access ebay data for a list of CPUs, GPUs, and Motherboards.")# Note that the first time this web application is loaded, it may take several minutes to search for all the data, though this will be retained on subsequent loads. ")
st.write("If you find this app useful and would like new parts to be added send me a message on LinkedIn! https://www.linkedin.com/in/gossdante/")
# st.write('To get newly updated data, press the "Rerun" button in the menu bar above.')
#st.write('Click the buttons below to load recent price data')

#d = 1
#if st.checkbox('Load All Data'):
#    st.write('CPU Search')
#    bar1 = st.progress(0)
cpu = cpu_scraper()
cpu_desc = cpu.groupby(['search_term'])['price'].describe()
    
#    st.write('CPU Done')
#    st.write('---')
#    st.write('GPU Search')
#    bar2 = st.progress(0)
gpu = gpu_scraper()
gpu2 = gpu.groupby(['search_term'])['price'].mean()
gpu3 = gpu.groupby(['search_term'])['price'].median()
gpu4 = gpu.groupby(['search_term'])['price'].min()
gpu5 = gpu.groupby(['search_term'])['price'].max()
gpu_desc = gpu.groupby(['search_term'])['price'].describe()

#    
#    st.write('GPU Done')
#    st.write('---')
#    st.write('Motherboard Search')
#bar3 = st.progress(0)
mboard = mboard_scraper()
mboard2 = mboard.groupby(['search_term'],as_index=False)['price'].mean()
mboard_desc = mboard.groupby(['search_term'],as_index=False)['price'].describe()
    
#    st.write('Motherboard Done')

dis = st.selectbox('Display Detailed Data', ['cpu','gpu','mboard'],index=None)

if dis == 'cpu':
    st.dataframe(cpu_desc)
elif dis == 'gpu':
    st.dataframe(gpu_desc)
elif dis == 'mboard':
    st.dataframe(mboard_desc)
#if st.checkbox('Get CPU Benchmarks'):
cpu_mark = cpu_marks()
#    st.dataframe(cpu_marks)
#    st.write('Done')
    
#if st.checkbox('Get GPU Benchmarks'):
gpu_mark = gpu_marks()
#    st.dataframe(gpu_marks)
#    st.write('Done')
    
#if st.checkbox('Get CPU Data'):
#    bar1 = st.progress(0)
#    cpu = cpu_scraper()
#    cpu['price'] = cpu['price'].apply(pd.to_numeric)
cpu2 = cpu.groupby(['search_term'])['price'].mean()

#    st.dataframe(cpu2)

#if st.checkbox('Get GPU Data'):
#    bar2 = st.progress(0)
#    gpu = gpu_scraper()
#    st.dataframe(gpu)
    
    
#if st.checkbox('Get Motherboard Data'):
#    bar3 = st.progress(0)
#    mboard = mboard_scraper()
#    st.dataframe(mboard)



st.write('---')

st.write("CPUs")
cpu_pp = pd.merge(cpu_mark,cpu2,left_on=['cpu_name'],right_on='search_term')
cpu_pp['Ratio'] = cpu_pp['cpu_marks']/cpu_pp['price']
cpu_pp['price'] = cpu_pp['price'].round(2)
cpu_pp['Ratio'] = cpu_pp['Ratio'].round(2)
cpu_pp = cpu_pp.rename(columns={'cpu_name' : 'CPU Name',
                       'cpu_marks' : 'CPU Benchmark Score',
                       'price' : 'Average Price (USD)',
                       'Ratio' : 'Price to Performance Ratio'})
st.dataframe(cpu_pp)

st.write("GPUs")
#
#st.dataframe(gpu2)
gpu_mark['join'] = gpu_mark['gpu_name'].str.split().str[1:].apply(' '.join)
#st.dataframe(gpu_mark)
gpu_pp = pd.merge(gpu_mark,gpu2,left_on=['join'],right_on=['search_term'])
gpu_pp['Ratio'] = gpu_pp['gpu_marks']/gpu_pp['price']
gpu_pp['Ratio'] = gpu_pp['Ratio'].round(2)
gpu_pp['price'] = gpu_pp['price'].round(2)

gpu_pp = gpu_pp.rename(columns={'gpu_name' : 'GPU Name',
                                'gpu_marks' : 'GPU Benchmark Score',
                                'price' : 'Average Price (USD)',
                                'Ratio' : 'Price to Performance Ratio'})
gpu_pp = gpu_pp.drop(columns=['join'])
st.dataframe(gpu_pp)


st.write("Motherboards")
mboard2 = pd.DataFrame(mboard2)
#mboard2.index = range(12)
mboard2['price'] = mboard2['price'].round(2)
mboard2 = mboard2.rename(columns={'search_term' : 'Motherboard Name',
                                  'price' : 'Average Price (USD)'})
mboard2['Motherboard Name'] = mboard2['Motherboard Name'].str.title()
st.dataframe(mboard2)
#if st.checkbox('CPU Price Performance'):
#    d=pd.merge(cpu_mark,cpu2,left_on=['cpu_name'],right_on='search_term')
#    d['Ratio'] = d['cpu_marks']/d['price']
#    d = d.sort_values(by='Ratio')
#    st.dataframe(d)
st.write('---')
st.write('Select any CPU or GPU from the tool below, a table will be created allowing you to fill in prices to get an updated Price to Performance Ratio.')
# Now I want to make a fill in the blank calculator for price to performance
# Combine cpu_marks & gpu_marks
gpu_pp2 = gpu_pp.rename(columns={'GPU Name' : 'Part Name',
                                'GPU Benchmark Score' : 'Benchmark Score'})
cpu_pp2 = cpu_pp.rename(columns={'CPU Name' : 'Part Name',
                       'CPU Benchmark Score' : 'Benchmark Score'})
marks = [cpu_pp2, gpu_pp2]
all_marks = pd.concat(marks)
parts = all_marks['Part Name'].drop_duplicates()
chosen_part = st.selectbox('Select a part of interest',parts)
number = st.number_input("Insert a number", value=None, placeholder="Type a number...")
temp_df = all_marks[all_marks['Part Name']==(chosen_part)]
#temp_df.index=['Part']
temp_df['User Price Input'] = number
#temp_df.iloc[0,4] = number
temp_df['New Price to Performance Ratio'] = temp_df['Benchmark Score']/temp_df['User Price Input']
#temp_df.iloc[0,5] = temp_df['Benchmark Score']/temp_df['User Price Input']

st.dataframe(temp_df)
#og_pp = temp_df['Price to Performance Ratio']
#new_pp = temp_df['New Price to Performance Ratio']
#diff_pp = og_pp - new_pp
#new = (new_pp[0],' Ratio based on Input')
#st.write(new)
#diff = (diff_pp,' Change from average')
#st.write(diff)

#st.metric(label=chosen_part, 
#          value=str(new_pp), 
#          delta=str(diff_pp)
#)

#cpu_mark2 = cpu_mark.rename(columns={'cpu_name':'Part',
#                                    'cpu_marks':'Benchmark'})
#gpu_mark2 = gpu_mark.rename(columns={'gpu_name':'Part',
#                                    'gpu_marks':'Benchmark'})
#gpu_mark2 = gpu_mark2.drop(columns=['join'])
#marks2 = [cpu_mark2, gpu_mark2]
#all_marks2 = pd.concat(marks2)
#parts2 = all_marks2['Part'].drop_duplicates()
#chosen_parts2 = st.selectbox('Select a part of interest', parts2)
#number = st.number_input("Insert a number", value=None, placeholder="Type a number...")
#temp_df = all_marks2[all_marks2['Part']==(chosen_parts2)]
#temp_df['User Price Input'] = number
#temp_df['Price to Performance Ratio'] = temp_df['Benchmark']/temp_df['User Price Input']
#st.dataframe(temp_df)





#st.data_editor(all_marks[all_marks['Part Name'].isin(chosen_parts)],
#               hide_index=True)




st.write('---')
if st.button('Get Updated Data (This will take a few moments)'):
    st.cache_data.clear()
    st.rerun()
