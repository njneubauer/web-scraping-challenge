from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Initialize chrome browser function
def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)

# NASA Mars News Scrape
def scrape():
    browser = init_browser()
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    time.sleep(2)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # retreive news title & news paragraph text
    news_div = soup.find_all('div', class_='content_title')
    for div in news_div[:2]:
        try:
            news_title = div.find('a').text
        except:
            pass
    news_p = soup.find('div', class_='article_teaser_body').text

     # set up splinter with url for scraping
    space_img_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    img_url_prefix = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    browser.visit(space_img_url)
    time.sleep(2)
    space_img_html = browser.html
    soup = BeautifulSoup(space_img_html, 'html.parser')

    # find featured image
    img_result = soup.find('img',class_='headerimage')
    # attach full url to image & print link
    feat_image_url = img_url_prefix + img_result['src']

    # Mars Facts Table Scrape to HTML string
    table_url = 'https://space-facts.com/mars/'
    mars_table_html = pd.read_html(table_url, attrs={'id':'tablepress-p-mars-no-2'})

    # Mars table to HTML string
    mars_df = mars_table_html[0]
    mars_df = mars_df.rename(columns={0:"",1:"Mars"})
    mars_df.reset_index(drop=True, inplace=True)
    mars_df_html = mars_df.to_html(index=False)
    mars_html_split = mars_df_html.split("\n")
    mars_html = [t for t in mars_html_split]
    mars_html[0]='<table id="table" class="dataframe table-striped">'
    glue = "\n"
    mars_html = glue.join(mars_html)

    # Mars Hemispheres
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    time.sleep(2)
    hem_html = browser.html
    hem_soup = BeautifulSoup(hem_html,'html.parser')
    
    
    hem_img_urls = []
    hem_divs = hem_soup.find_all('div',class_='description')
    for div in hem_divs:
        img_title = div.find('a').text
        try:
            browser.click_link_by_partial_text(img_title)
            time.sleep(1)
            browser.click_link_by_text('Sample')
        except:
            print('not found')
        # Grab new window url
        new_url = browser.windows[1].url
        # Close new window
        browser.windows[1].close()
        # Visit new url
        browser.visit(new_url)
        # Grab html and image src url
        html = browser.html
        soup = BeautifulSoup(html,'html.parser')
        img_tag = soup.find('img')
        full_img = img_tag['src']
        # save url to list
        split = img_title.split(" ", -1)
        del split[-1]
        img_title = (" ").join(split)
        hem_dict = {
            'title': img_title,
            'img_url': full_img
        }
        hem_img_urls.append(hem_dict)
        # Go back to page with mars image list
        browser.back()
        browser.back()

    
    # Dictionary to hold scraped information
    scrape_info = {
        'featured_img': feat_image_url,
        'news_title': news_title,
        'news_p': news_p,
        'mars_table': mars_html,
        'hemisphere_urls':{
                'title':[],
                'url':[]
        }
    }
    for d in hem_img_urls:
        scrape_info['hemisphere_urls']['title'].append(d['title'])
        scrape_info['hemisphere_urls']['url'].append(d['img_url'])
    
    browser.quit()
    
    return scrape_info