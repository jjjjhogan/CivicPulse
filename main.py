from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


def main():
    # Set up Chrome options to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, use_subprocess=False, version_main=149)

    # Define the universities and their respective URLs
    universities = {
        'UCLA': "https://registrar.ucla.edu/faculty-staff/classrooms-and-scheduling/building-list"
    }

    google_url = 'https://www.google.com'

    # Loop through universities
    for university, URL in universities.items():
        # Make a request to the university's building list page
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')

        # Extract building information
        buildings = soup.findAll('td')
        for b in buildings:
            try:
                print(b.text)

                # Search for the building on Google
                driver.get(f'{google_url}/search?q={b.text} {university} building')

                # Find the first search result link
                div = driver.find_element(By.XPATH, '//a[@jsname="UWckNb"]')
                print(div.get_attribute('href'))
                href = div.get_attribute('href')

                # Visit the Google search result page
                driver.get(href)

                # Extract and print image URLs from the page
                imgs = driver.find_elements(By.XPATH, '//img')
                for img in imgs:
                    print(img.get_attribute('src'))

            except Exception as e:
                print(e)

    # Close the browser
    driver.quit()


if __name__ == '__main__':
    main()
