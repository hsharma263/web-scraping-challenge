from bs4 import BeautifulSoup
import requests
import pymongo
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template
from flask_pymongo import PyMongo

def init_browser():
    executable_path = {"executable_path": ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_dict = {}


    # NASA MARS NEWS
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    news_title = soup.find_all("div", class_="content_title")[0].text.strip()
    news_p = soup.find_all("div", class_="rollover_description_inner")[0].text.strip()


    # JPL MARS SPACE IMAGES
    jpl_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
    jpl_site_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/"
    browser.visit(jpl_url)

    html = browser.html
    soup2 = BeautifulSoup(html, "html.parser")  
    featured_image = soup2.find_all("img")[1]["src"]
    featured_image_url = jpl_site_url + featured_image


    # MARS FACTS
    facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(facts_url)
    mars_facts = tables[2]
    mars_facts.columns=["Characteristic", "Value"]
    html_table_mars = mars_facts.to_html()
    html_table_mars = html_table_mars.replace('\n', '')

    # MARS HEMISPHERES
    main_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(main_url)
    main_site_html = browser.html
    main_site_soup = BeautifulSoup(main_site_html, "html.parser")
    hemi_views = main_site_soup.find("div", class_="collapsible results").find_all("div", class_="item")

    hemisphere_image_urls = []
    hemi_image_dict = {}
    usgs_url = "https://astrogeology.usgs.gov/"

    for i in hemi_views:
        try:
            title = i.h3.text
            url_snip = i.a["href"]
            
            image_url = usgs_url + url_snip
            
            hemi_image_dict["title"] = title
            hemi_image_dict["img_url"] = image_url
            
            hemisphere_image_urls.append(hemi_image_dict)

        except Exception as e:
            print(e)


    mars_dict={
        "news_title:": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "Mars_facts_table": html_table_mars,
        "hemisphere_images": hemisphere_image_urls 
    }

    browser.quit()
    return mars_dict