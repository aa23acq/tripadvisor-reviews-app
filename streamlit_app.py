import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Function to scrape data from the provided URL using Selenium
def scrape_data(url):
    try:
        # Set up the Selenium WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        driver.get(url)


        # Wait for the URL to match
        wait.until(EC.url_to_be(url))
        print("Please solve the CAPTCHA within the next 40 seconds...")
        time.sleep(10)
        # Find parent div containing all reviews
        parent_div = driver.find_element(By.XPATH, "//div[contains(@class, 'uqMDf') and contains(@class, 'z') and contains(@class, 'BGJxv') and contains(@class, 'xOykd') and contains(@class, 'jFVeD') and contains(@class, 'yikFK')]")
        print(parent_div)
        # Extract reviews
        reviews = []
        review_elements = parent_div.find_elements(By.XPATH, ".//div[contains(@class, 'azLzJ') and contains(@class, 'MI') and contains(@class, 'R2')]")
        print(review_elements)
        for review in review_elements:
            author = review.find_element(By.XPATH, ".//a[contains(@class, 'BMQDV')]").text
            print(author)
            date = review.find_element(By.XPATH, ".//span[contains(text(), 'wrote a review')]").text.split('wrote a review')[1].strip()
            print(date)
            location = driver.find_element(By.XPATH, "//span[contains(@class, 'xLwBc') and contains(@class, 'S2') and contains(@class, 'H2') and contains(@class, 'Ch') and contains(@class, 'd')][1]").text
            print(location)
            contributions = driver.find_element(By.XPATH, "//span[contains(@class, 'xLwBc') and contains(@class, 'S2') and contains(@class, 'H2') and contains(@class, 'Ch') and contains(@class, 'd')][2]").text
            print(contributions)
            helpful_votes = driver.find_element(By.XPATH, "//span[contains(@class, 'xLwBc') and contains(@class, 'S2') and contains(@class, 'H2') and contains(@class, 'Ch') and contains(@class, 'd')][3]").text
            print(helpful_votes)
           
           
            title = review.find_element(By.XPATH, ".//div[@data-test-target='review-title']/a/span").text
            print(title)
            text = review.find_element(By.XPATH, ".//div[contains(@class, 'fIrGe')]//span").text
            print(text)
            date_of_stay = review.find_element(By.XPATH, "//span[contains(text(), 'Date of stay:')]").text.split(': ', 1)[1]
            print(date_of_stay)

            reviews.append({
                "author": author,
                "date": date,
                "location": location,
                "contributions": contributions,
                "helpful_votes": helpful_votes,
                "title": title,
                "text": text,
                "date_of_stay": date_of_stay
            })

        # Clean up
        driver.quit()

        return reviews

    except Exception as e:
        driver.quit()
        print(e)
        return f"An error occurred: {str(e)}"

# Streamlit app code
st.title("Web Scraping with Selenium")

# User input for URL
url = st.text_input("Enter the URL of the page to scrape:")

if st.button("Scrape Data"):
    if url:
        with st.spinner("Scraping..."):
            reviews = scrape_data(url)
            print(reviews)
        if isinstance(reviews, list) and reviews:
            st.subheader("Reviews")
            # Convert reviews to DataFrame
            reviews_df = pd.DataFrame(reviews)
            
            # Display reviews in a table
            st.dataframe(reviews_df)
            
            # Provide CSV download
            csv = reviews_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name='reviews_data.csv',
                mime='text/csv'
            )
        else:
            st.write("No reviews found or an error occurred.")
    else:
        st.warning("Please enter a valid URL.")
