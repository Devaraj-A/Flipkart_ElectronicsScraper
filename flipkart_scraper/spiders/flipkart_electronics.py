import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import re
import pandas as pd
import logging

class FlipkartElectronicsSpider(scrapy.Spider):
    name = "flipkart_electronics"
    allowed_domains = ["flipkart.com"]

    def __init__(self, *args, **kwargs):
        super(FlipkartElectronicsSpider, self).__init__(*args, **kwargs)
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.dr = webdriver.Firefox(options=options)
        df = pd.DataFrame({'Product Name':[],'Price':[],'Discount Percentage':[],'Currency':[],'Rating':[],'Number of Reviews':[],'Availability Status':[],'Seller Information': [],'Product URL':[]})     
        count = 0
        try:
            for n in range(1, 6):
                self.driver.get(f'https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g&otracker=categorytree&fm=neo%2Fmerchandising&iid=M_03c6dcc6-c8ba-43dc-a102-72ddf4dd676e_1_372UD5BXDFYS_MC.F6KJFVU7EOGS&otracker=hp_rich_navigation_1_1.navigationCard.RICH_NAVIGATION_Electronics%7ELaptop%2Band%2BDesktop%7EAll_F6KJFVU7EOGS&otracker1=hp_rich_navigation_PINNED_neo%2Fmerchandising_NA_NAV_EXPANDABLE_navigationCard_cc_1_L2_view-all&cid=F6KJFVU7EOGS&page={n}')
                
                self.products = self.driver.find_elements(By.XPATH, "//div[@class='tUxRFH']")
                
                for pro in self.products:
                    try:
                        count += 1
                        price = pro.find_element(By.XPATH, ".//div[@class='Nx9bqj _4b5DiR']").text
                        price = price.replace('₹','')
                        discount_percentage = pro.find_element(By.XPATH, ".//div[@class='UkUFwK']//span").text
                        discount_percentage = discount_percentage.replace(' off','')
                        currency = "INR"
                        try:
                            rating = pro.find_element(By.XPATH, ".//div[@class='XQDdHH']").text
                        except:
                            rating = ''
                        try:
                            number_of_reviews = pro.find_element(By.XPATH, ".//span[@class='Wphh3N']").text
                        except:
                            number_of_reviews = ''
                        number_of_reviews = number_of_reviews.split('& ')
                        number_of_reviews = number_of_reviews[-1].split(' ')
                        number_of_reviews = number_of_reviews[0]
                        
                        try:
                            availability_status = pro.find_element(By.XPATH, ".//div[@class='col col-5-12 BfVC2z']").text
                            pattern = r'Only\s(.+)\sleft'
                            match = re.search(pattern, availability_status)
                            availability_status = match.group() if match else "Available"

                        except:
                            availability_status = ''
                        
                        product_URL = pro.find_element(By.XPATH, ".//a[@class='CGtC98']").get_attribute('href')
                        
                        self.dr.get(product_URL)
                        product_name = self.dr.find_element(By.XPATH, "//span[@class='VU-ZEz']").text
                        try:
                            seller_name = self.dr.find_element(By.XPATH, "//div[@id='sellerName']//span//span").text
                        except:
                            seller_name = ''
                        
                        df = df._append({'Product Name': product_name,
                                        'Price': price,
                                        'Discount Percentage': discount_percentage,
                                        'Currency': currency,
                                        'Rating': rating,
                                        'Number of Reviews': number_of_reviews,
                                        'Availability Status': availability_status,
                                        'Seller Information': seller_name,
                                        'Product URL': product_URL}, ignore_index=True)
                        
                        logging.info(f'Found product - Name: {product_name}, Price: {price}, Discount: {discount_percentage}, Currency: {currency}, Rating: {rating}, Reviews: {number_of_reviews}, Availability: {availability_status}, URL: {product_URL}')
                        if count == 100:
                            break

                    except Exception as e:
                        logging.error(f'Error processing a product: {e}')
                        
        except Exception as e:
            logging.error(f'Error loading page {n}: {e}')    

        df.to_csv('Flipkart.csv', index=False)
        logging.info('Data saved to Flipkart.csv')