import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to scrape content from TripAdvisor
def scrape_tripadvisor(url):
    # Setup options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open the URL
    driver.get(url)

    try:
        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.some-content-selector"))  # Update the selector as needed
        )
        # Extract page content
        content = driver.page_source
    except Exception as e:
        content = f"Error occurred: {str(e)}"
    finally:
        driver.quit()

    return content

# Streamlit app
st.title("TripAdvisor Content Scraper")

url = st.text_input("Enter TripAdvisor URL:")

if st.button("Scrape"):
    if url:
        with st.spinner("Scraping content..."):
            content = scrape_tripadvisor(url)
            st.text_area("Page Content", content, height=400)
    else:
        st.error("Please enter a URL.")
