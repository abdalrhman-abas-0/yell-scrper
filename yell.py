from time import sleep
import datetime
import os
from tqdm import tqdm
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
Firefox_options = Options()
Firefox_options.add_argument("--start-maximized")
# %% Inputs.

pages_to_scrape = 10
record_file = "no"
search_subject = "architects"
search_location = "london"

# %% defining the chrome browser

driver = webdriver.Firefox()
actions = ActionChains(driver)

# changing the directory to yell folder
# using try and except will not through
# errors when debugging
try:
    os.chdir("yell")
except:
    pass
# %% main variables

# the main page url
url = "https://www.yell.com/?utm_source=byc&utm_medium=referral&utm_campaign=top-black-bar"

# the the name of the website being scraped
website = 'yell'

primary_stage = True
'''if true it enables the run of the primary stage, and it's False then the program will continue 
and concatenate all the individual files and saves it as one file.'''

nap = 5
'''the sleep time in seconds between the requests.'''

p_save_index = 0
'''the number of the last saved primary file
(incase of building upon old uncompleted scaping ), it's zero for 
'''

I_P = 0
'''the the index of the last successfully scraped search page "primary stage".'''

fist_scraped_page = True
"""when it's true the url of the fist scraped page will be written in the txt file"""

build_upon_previous = False
""" building upon an previous scraping project."""

# %% txt tracker File

# if there a record file were given it resets the MAIN variables above to continue upon the previous scraping process,
# and if record file was given as 'no' it leave them to their default values to start a new scraping process.

if record_file.lower() != 'no':
    txt_tracker = record_file
else:
    date_time = str(f'{datetime.datetime.now()}')[
        :f'{datetime.datetime.now()}'.index('.')].replace(':', '.')
    txt_tracker = f'tracker {search_subject} in {search_location} at {date_time}.txt'
    first_creation = open('./outputs/' + txt_tracker, "w")
    first_creation.close()

try:
    with open('./outputs/' + txt_tracker, 'r') as file:
        file = file.readlines()
        '''an txt file which records the progress of the scraping process'''
        for line in file:

            if 'primary.csv' in line:
                # as every pages saved in it's own csv file the save index and
                # the I_P which is the last page scraped successfully are the same
                p_save_index = I_P = int(
                    re.search(f'(?!{search_location} )\d+', line)[0])
                build_upon_previous = True

            # ensuring that the end result file isn't already saved.
            elif line.strip("\n") == f"{website} {search_subject} in {search_location}.csv":
                build_upon_previous = False

        fist_scraped_page = False
except:
    pass

# %% crawler Function


def crawler(site: str, element: str, as_check_url: bool):
    """ ensures that the correct page is landed on
    it can be used in to ways:
    first mode as_check_url = True:
        it will check for the current url if it matches the check_url 
        "site" every second for 10 seconds then it will look for 
        the given element and if it's not found it will notify the 
        developer to navigate to the given site
    second mode as_check_url = False: 
        it will keeps making requests for the given site until landing
        on the desired page then, it knows that through looking for 
        the given element.
    in both cases if the servers redirected the program to another page or 
    to a bot detection test, in such case the function will notify the
    developer of a problem as the developer must resolve it manually 
    and enter 'y' in the input box.

    Args:
        site (str): _the url of the desired page.Defaults to "link".
        element (str): the ID or CSS SELECTOR of the element to look for.
        as_check_url (bool): if True thr function will be ran in 
            it's first mode and use the site as a check_url.

    Returns:
        key_element (selenium.webdriver.remote.webelement.WebElement):
            the element to look for on the page. 
    """
    if as_check_url == False:
        while True:
            try:
                driver.get(site)
                # if any of the given characters are 
                # in element then use the css
                if '.' in element or '#' in element or '=' in element :
                    key_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, element)
                        )
                    )
                else:
                    key_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.ID, element)
                        )
                    )
                sleep(nap)
                # checking if the page is the requested page
                if site == driver.current_url:
                    break
            except:
                while (input("browser problem please resolve it manually and enter'y'.")).lower() != 'y':
                    sleep(1)
    else:
        check_url = site
        while True:
            try:
                # waiting up to 10 seconds for the page to load before
                # searching for the key_element
                waiting_time = 0
                while driver.current_url != check_url:
                    print("current", driver.current_url)
                    print("check", check_url)
                    sleep(1)
                    waiting_time += 1
                    # breaking the loop after 11 seconds
                    if waiting_time == 11:
                        print("passed")
                        break

                # thronging an error if the waiting time exceeds 10 seconds
                # to go directly to the exception without looking for the
                # key_element
                if waiting_time >= 10:
                    print(throwing_an_error_on_purpose)

                # the result list of search results available on the page
                key_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, element)))
                break
            except:
                while (input(f"""browser problem please resolve it manually and ensure that the page url is \n "{site}" \n then enter'y' to continue.""")).lower() != 'y':
                    sleep(1)

    return key_element

# %% Data Frame Builder Function


def df_builder(search_subject: str, search_location: str):
    """ the DataFrame Builder
    it looks for a saved primary csv file in the "record_file"
    given in the inputs to continue from it, and if it didn't find it
    it concatenates the individually saved primary/secondary csv files
    to one df and save it as one csv file.

    Args:
        search_subject (str): the subject of the search, used to 
            find the PRIMARY/SECONDARY file.
        search_location (str): the location of the search, used to 
            find the PRIMARY/SECONDARY file.

    Returns:
        df_ (pandas.DataFrame): a pandas DataFrame which is save as a csv file.

    """
    with open('./outputs/' + txt_tracker, 'r') as file:

        for line in file:

            if f'1 primary' in line:
                df_0 = pd.read_csv('./outputs/' + str(line).strip('\n'))
                continue

            elif 'https://' not in line and 'primary' in line:
                df_ = pd.concat([df_0, pd.read_csv(
                    './outputs/' + str(line).strip('\n'))], axis=0, ignore_index=True)
                df_0 = df_

    df_ = df_.drop_duplicates()
    df_.to_csv('./outputs/' +
               f"{website} {search_subject} in {search_location}.csv", index=False)

    with open('./outputs/' + txt_tracker, 'a') as file:
        file.write('\n')
        file.write(f"{website} {search_subject} in {search_location}.csv")

    return df_

# %% Navigating To The Search Results & Getting The Number Of Available Pages.

# this part looks for the number of pages available on the scraped site for a
# given subject and location and adjusts the number of pages_to_scrape accordingly.
# the response of this page in case of a new scraping process will be used to
# scrape the data for the fist page in the primary stage.


# input the search_subject into the search_bar
search_bar = crawler(url, 'search_keyword', False)
search_bar.click()
search_bar.send_keys(search_subject)

# input the search_location into the location_bar
location = driver.find_element(By.ID, 'search_location')
search_location_0 = location.get_attribute('value')
location.click()
location.clear()
location.send_keys(search_location)

# pressing the search button in the website to initiate the search
driver.switch_to.default_content()
find = driver.find_element(
    By.CSS_SELECTOR, 'button[aria-label="Search now"]')
ActionChains(driver).move_to_element(find).perform()

try:
    accept_cookies = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[2]/button/strong'
             )
        )
    )
    accept_cookies.click()
    driver.switch_to.default_content()
except:
    pass

find.click()

# primary search page done
sleep(5)

# number of available results for a search
try:
    # returns the number of results available for a given search
    search_pages_available_E = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'nav[aria-label="Pagination"]')
        )
    )
    search_pages_available = int(search_pages_available_E.find_elements(
        By.CSS_SELECTOR, 'a[class="btn btn-grey"]')[-1].text)
except:
    # in case of an exception that means that the search
    # have only one result page for that search
    search_pages_available = 1

print(f'{search_pages_available} pages available.')

pages_to_scrape = list(range(1, pages_to_scrape + 1))

if len(pages_to_scrape) > search_pages_available:
    pages_to_scrape = pages_to_scrape[:search_pages_available + 1]

# %% Primary Scraper variables

result_list = []
"""contains the scraped info from the primary stage"""

results_scraped = 0
"""counts the scraped pages."""

next = False
"""dictates if the primary scraper will starts scraping using the same response 
    used to get the results_available above or not
"""


# %% Primary Scraper

# this part "primary stage" scrapes each page and saves its outputs in csv file.
# it scrapes the profiles names and the business names.
if primary_stage == True or len(pages_to_scrape) > I_P:

    check_url = driver.current_url
    """used to check that the driver is on the right page when a problem occurs."""

    # navigating to the page after the last page scraped to continue scraping it
    if build_upon_previous == True:
        page_acquired = False

        # checks if the scraper starts from the page after the last page it scraped.
        while page_acquired == False:
            # going to the next page through pressing the next button on the search results page
            driver.switch_to.default_content()
            ActionChains(driver).send_keys(Keys.END).perform()

            pagination = crawler(
                check_url, 'a[data-tracking="DISPLAY:PAGINATION:NUMBER"]', True)

            # checking which pagination button directs the program to the desired page
            for button in pagination:

                # adding one to the I_P to scrape the page after the last
                # scraped page
                if int(button.text) == I_P + 1:
                    check_url = button.get_attribute('href')
                    button.click()
                    driver.switch_to.default_content()
                    page_acquired = True
                    break

                # if the desired page is not found then go to the last page then
                # the loop will continue searching for the desired page again
                # after going to the last page available in the pagination
                elif button is pagination[-1]:
                    check_url = button.get_attribute('href')
                    button.click()
                    driver.switch_to.default_content()

    # iterating through the result pages to scrape them
    for Page in tqdm(pages_to_scrape[I_P:], unit="page", ncols=110, colour='#0A9092'):

        # a list of all the info except the title and url for
        # all the results available on the result page
        primary_info = crawler(
            check_url, 'div[class="row businessCapsule--mainRow"]', True)

        # a list of the business by title and url
        business_titles = crawler(
            check_url, 'a[class="businessCapsule--title"]', True)

        sleep(1)

        # iterates through the results
        for info, title in zip(primary_info, business_titles):

            sleep(0.02)
            # skipping the sponsored results
            try:
                title.find_element(
                    By.CSS_SELECTOR, "p.businessCapsule--sponsored")
                continue
            except:
                pass

            # setting the scraped info to not available in case they are not found
            catagories = phone = address = rating = reviews = "not available"

            # business name
            try:
                business = title.find_element(
                    By.CSS_SELECTOR, 'h2[class="businessCapsule--name text-h2"]') .text
            except:
                print(title.text)

            # business's yell profile link
            business_profile = title.get_attribute("href")

            # gets the business address
            try:
                address = info.find_element(
                    By.CSS_SELECTOR, 'span[itemprop="address"]').text
            except:
                pass

            # the catagories that the business falls into
            try:
                catagories_E = info.find_element(
                    By.CSS_SELECTOR, 'div[class="col-sm-17 col-md-16 col-lg-18 businessCapsule--classStrap"]')
                catagories = catagories_E.text
            except:
                pass

            # getting the phone number through pressing on the phone icon
            try:
                phone_E = info.find_element(
                    By.CSS_SELECTOR, 'span[class="icon icon-phone business--telephoneIcon"]')
                phone_E.click()
                # extracting the phone number
                phone = info.find_element(
                    By.CSS_SELECTOR, 'span.business--telephoneNumber').text
            except:
                pass

            # average rating by customers and the review count
            try:
                rating = float(info.find_element(By.CSS_SELECTOR,
                               'span.starRating--average').text)
                reviews = int(info.find_element(By.CSS_SELECTOR,
                              'span.starRating--total').text)
            except:
                pass

            # contains the scraped individual results
            result = {
                "Business Name": business,
                "Profile": business_profile,
                "Catagories": catagories,
                "Phone Number": phone,
                "Address": address,
                "Rating": rating,
                "Reviews": reviews
            }

            # replaces empty strings in the result dict with "Not listed"
            for key, value in result.items():
                if value == '':
                    result[key] = "Not Listed"

            result_list.append(result)

        results_scraped += len(result_list)

        p_save_index += 1

        p_df = pd.DataFrame(result_list)
        p_df.to_csv(
            './outputs/' + f"{website} {search_subject} in {search_location} {p_save_index} primary.csv", index=False)

        try:
            file = open('./outputs/' + txt_tracker, 'a')
        except:
            file = open('./outputs/' + txt_tracker, 'w')

        current_page = driver.current_url

        if fist_scraped_page == True:
            # writing the url of the first scraped page to use it later as a
            # start point if the the scraping didn't go wright from the first time
            current_page += "first_search_page"
            fist_scraped_page = False

        file.write('\n')
        file.write(
            f"{website} {search_subject} in {search_location} {p_save_index} primary.csv")
        file.write('\n')
        file.write(current_page)
        file.close()

        # emptying the result list after saving it's contents
        result_list = []

        I_P = Page

        # going to the next page through pressing the next button on the search results page
        try:
            driver.switch_to.default_content()
            ActionChains(driver).send_keys(Keys.END).perform()

            next_page = driver.find_element(
                By.CSS_SELECTOR, 'a[data-tracking="DISPLAY:PAGINATION:NEXT"]')
            check_url = next_page.get_attribute('href')
            next_page.click()
            driver.switch_to.default_content()
        except:
            print('no more pages available !!')
            break

    print(
        f"primary is done, {results_scraped + len(result_list)} results Scraped successfully !!")

    driver.quit()
else:
    print('primary stage is already completed.')


# %% building the final DataFrame

# building the end result DataFrame, inspect it's contents, save it as csv file
# & delete the individually saved primary csv files used in it's construction
# along with the txt tracker file.

df = df_builder(search_subject, search_location)

print('\n' * 3, df.info(), '\n' * 3)

print(df.tail(), '\n')

files = os.listdir('./outputs/')
for file in files:
    if 'primary' in file or txt_tracker in file:
        os.remove('./outputs/' + file)

print('scraping is concluded successfully.')
