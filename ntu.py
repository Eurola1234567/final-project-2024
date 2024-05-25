# -*- coding: utf-8 -*-
"""
Created on Sat May 18 09:45:22 2024

@author: SHIH-SIANG, HUNG
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd


# set the file name
filename = "data.csv"

def clean_empty_rows(data):
    """
    clean the empty row if it exists
    """
    return data.dropna(how='all')

# try to lead the data in, if not, create a new list (will occur at the very first try)
try:
    existing_data = pd.read_csv(filename)
    existing_data = clean_empty_rows(existing_data)
    existing_links = existing_data['Link'].tolist()
    links = existing_links.copy()
    titles = existing_data['Title'].tolist()
    categories = existing_data['Category'].tolist()
    dates = existing_data['Release Date'].tolist()
    is_new = [False] * len(links)
    
except FileNotFoundError:
    links = []
    titles = []
    categories = []
    dates = []
    is_new = []

# make a request 
response = requests.get('https://career.ntu.edu.tw/board/index/tab/0')
soup = BeautifulSoup(response.text, "html.parser")

# find all target we want
announcement_items = soup.find_all('li', class_='announcement-item')
flip = 0

# iteration 
for item in announcement_items:
    # Find the <a> tag within the <h5> tag
    h5_tag = item.find('h5')
    link = h5_tag.find('a')['href'] if h5_tag else None
    if link:
        if link in links:
            # if the link already exists, just change the flip to False 
            idx = existing_links.index(link)
            flip += 1 
        else:
            # append new data 
            links.append(link)
            
            # make a request to the detail page
            detail_response = requests.get(link)
            detail_soup = BeautifulSoup(detail_response.text, "html.parser")
            
            # get the title
            detail_title = detail_soup.title.string if detail_soup.title else 'No title found'
            detail_title = detail_title.split(' ')
            titles.append(' '.join(map(str, detail_title[4:])))
            
            # get the content 
            detail_content = detail_soup.get_text(separator="\n", strip=True)
            
         
        
            # get category
            tags_wrap = item.find('div', class_='tags-wrap')
            category_link = tags_wrap.find('a') if tags_wrap else None
            if category_link:
                category = category_link.get_text()
                categories.append(category)
            else:
                categories.append('')  #  no category found
        
            # get release date
            date_span = item.find('span', class_='date')
            if date_span:
                date = date_span.get_text(strip=True)
                dates.append(date)
            else:
                dates.append('')  #no date found
            
            # Mark this item as new
            is_new.append(True)

# If all the data are new (except the top one), flip the page to page two and do the same thing
if flip == 1:
    # make a request 
    response = requests.get('https://career.ntu.edu.tw/board/index/tab/0/page/2')
    soup = BeautifulSoup(response.text, "html.parser")

    # find all target we want
    announcement_items = soup.find_all('li', class_='announcement-item')
    
    # iteration 
    for item in announcement_items:
        # Find the <a> tag within the <h5> tag
        h5_tag = item.find('h5')
        link = h5_tag.find('a')['href'] if h5_tag else None
        if link:
            if link in links:
                # if the link already exists, just change the flip to False 
                idx = existing_links.index(link)
            else:
                # append new data 
                links.append(link)
                
                # make a request to the detail page
                detail_response = requests.get(link)
                detail_soup = BeautifulSoup(detail_response.text, "html.parser")
                
                # get the title
                detail_title = detail_soup.title.string if detail_soup.title else 'No title found'
                detail_title = detail_title.split(' ')
                titles.append(' '.join(map(str, detail_title[4:])))
                
                # get the content 
                detail_content = detail_soup.get_text(separator="\n", strip=True)
                
             
            
                # get category
                tags_wrap = item.find('div', class_='tags-wrap')
                category_link = tags_wrap.find('a') if tags_wrap else None
                if category_link:
                    category = category_link.get_text()
                    categories.append(category)
                else:
                    categories.append('')  #  no category found
            
                # get release date
                date_span = item.find('span', class_='date')
                if date_span:
                    date = date_span.get_text(strip=True)
                    dates.append(date)
                else:
                    dates.append('')  #no date found
                
                # Mark this item as new
                is_new.append(True)
                
# Combine the data 
final_data = pd.DataFrame({
    'Link': links,
    'Title': titles,
    'Category': categories,
    'Release Date': dates,
    'is_new': is_new
})

# Write data to CSV file
final_data.to_csv(filename, index=False, encoding='utf-8-sig')

print("CSV file saved as:", filename)
