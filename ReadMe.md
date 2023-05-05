# Yell scraper.

* this scraper is compiled in a way that avoids connection interruptions and enables the developer to pass the bot detection tests manually while the without interrupting the program.

* it scrapes the following information for lead generation and saves it in a .csv file.

## lead Information:

> Business Name

> Profile

> Catagories

> Phone Number

> Address

> Rating

> Reviews


## Inputs:

> pages_to_scrape: the number of search results pages to scrape.

> record_file: the name of the txt file that contains the scraping history, enter 'no' if a new scraping process to be started.

> search_subject: what to search for on the site.

> search_location: the location of the search.

## Files & Folders:

1. the outputs folder:
    contains all the scraped .csv files and the .txt tracker file.
2. tracker file:
   a .txt file records the progress of the scraping process and can be used to build up on uncompleted scraping from a previous time.
3. .csv files:
   a. primary files: individually scraped for each primary stage iteration.
   b. the final output file will be named in the following format ({site_name} {search_subject} in {search_location}.csv)

## Handling Interruptions:
if the program got blocked by the scraped site "yell" or redirected to a bot detection test it will notify the developer and ask to solve it manually and ensure that the current page url matches the url in the notification "if given" and after the problem is resolved manually the developer must enter 'y' so that the program continues.
