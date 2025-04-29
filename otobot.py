from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from datetime import datetime
import time
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv(override=True)
# Database configuration
DB_CONFIG = {
    'dbname': "postgres",
    'user': "postgres",
    'password': "mojehaslo",
    'host': "localhost",
    'port': "5432"
}

# Function to create database connection
def create_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

# Function to create table if it doesn't exist
def create_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id SERIAL PRIMARY KEY,
                price DECIMAL,
                area DECIMAL,
                voie VARCHAR(255),
                city VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        conn.rollback()

# Function to insert data into database
def insert_data(conn, price, area, voie, city):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO properties (price, area, voie, city) VALUES (%s, %s, %s, %s)",
            (price, area, voie, city)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error inserting data: {str(e)}")
        conn.rollback()

chrome_options = Options()  # Run in headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set window size


service = Service("C:/Users/wojci/Desktop/retardetai/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options) 
wait = WebDriverWait(driver, 10)

url = "https://www.otodom.pl"
driver.get(url)

place = 'Polska'
# Wait for and accept cookies
try:
    # First try to find the button by text
    cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Akceptuję')]")))
    cookie_button.click()
    print("Cookies accepted")
except Exception as e:
    print("Error accepting cookies:", str(e))

"""
search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="search.form.location.button"]')))
search_input.click()
search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="search.form.location.input"]')))
time.sleep(1) 
search_input.send_keys(city)
time.sleep(1)
search_input.send_keys(Keys.ENTER)
# Wait for the area filters to be present

"""
# Find and click the submit button
submit_button = wait.until(EC.element_to_be_clickable((By.ID, "search-form-submit")))
submit_button.click()
time.sleep(2)



prices = []
areas = []
voies = []
cities = []

# Initialize database connection
conn = create_connection()
if conn:
    create_table(conn)

# Function to scrape current page
def scrape_current_page():
    try:
        price_elements = driver.find_elements(By.XPATH, '//article[@data-cy="listing-item"]//span[@data-sentry-component="Price"]')
        area_elements = driver.find_elements(By.XPATH, '//article[@data-cy="listing-item"]//dt[normalize-space()="Powierzchnia"]/following-sibling::dd[1]/span')
        voie_elements = driver.find_elements(By.XPATH, '//article[@data-cy="listing-item"]//p[@data-sentry-component="Address"]')
        print(f"Found {len(price_elements)} price elements and {len(area_elements)} area elements")
        
        for price_element, area_element, voie_element in zip(price_elements, area_elements, voie_elements):
            try:
                full_text = voie_element.text
                parts = full_text.split(', ')
                voie_text = parts[-1].strip()
                city_text = parts[-2].strip()
                price_text = price_element.text.strip()
                area_text = area_element.text.strip()
                
                # Clean the price text (remove non-breaking spaces, 'zł', and all spaces)
                price_text = price_text.replace('\xa0', '').replace('zł', '').replace(' ', '').strip()
                # Clean the area text (remove 'm²')
                area_text = area_text.replace('m²', '').strip()
                
                # Insert into database
                if conn:
                    insert_data(conn, price_text, area_text, voie_text, city_text)
                    print(f"Inserted price: {price_text}, area: {area_text}, voie: {voie_text}, city: {city_text}")
            except Exception as e:
                print(f"Error processing elements: {str(e)}")
                if conn:
                    conn.rollback()
                continue
    except Exception as e:
        print(f"Error finding elements: {str(e)}")
        if conn:
            conn.rollback()

# Scrape first page
scrape_current_page()

# Handle pagination
page = 1
while page < 1000:
    try:
        # Try to find and click the next page button
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//li[@aria-label="Go to next Page"]')))
        if not next_button.is_enabled():
            print("No more pages available")
            break
            
        print(f"\nMoving to page {page + 1}")
        next_button.click()
        time.sleep(5)  # Wait for the new page to load
        
        # Scrape the new page
        scrape_current_page()
        page += 1
        
    except Exception as e:
        print(f"Error during pagination: {e}")
        break

# Close database connection
if conn:
    conn.close()

# Close the browser
driver.quit()
        
