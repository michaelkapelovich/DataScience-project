# Import necessary libraries. Selenium is used for web scraping,
# dataclasses for creating data structure, BeautifulSoup for parsing HTML,
# and pandas for data manipulation.
from selenium import webdriver
from dataclasses import dataclass, asdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Set the URL of the webpage you want to scrape.
# Also, define the starting page number.
PATH = "C:\Program Files (x86)\chromedriver.exe" 
URL = 'https://www.footballtransfers.com/en/players'
PAGE_NUM = 0

# Define a dataclass `Player` that will hold the data for each player.
# It's a convenient way to define classes which primarily store data.
@dataclass
class Player:
    Name: str = None
    Age: int = 0
    Nationality: str = None
    Height: int = 0
    Weight: int = 0
    Team: str = None
    Skill: float = 0.0
    Pot: float = 0.0
    Current_Fee: str = None
    Highest_xTV: str = None
    num_trophies: int = 0
    Preferred_foot: str = None
    Best_Playing_Role: str = None
    Season: str = None
    Matches_played: int = 0
    Minutes_played: float = 0.0
    Goals: int = 0
    Assists: int = 0
    Yellow_Cards: int = 0
    Red_Cards: int = 0
    Shots: float = 0
    Penalties: int = 0
    Expected_Goals: int = 0
    Attacking_Challenges: int = 0
    Passes: float = 0.0
    Key_Passes: int = 0
    Crosses: int = 0
    Offsides: int = 0
    Ball_Recoveries: int = 0
    Ball_Recoveries_Opponent: int = 0
    Challenges: int = 0
    Air_Challenges: int = 0
    Tackles: int = 0
    Ball_Interceptions: int = 0
    Lost_Balls: int = 0
    Lost_Balls_Own: int = 0
    Errors_to_Goal: int = 0

# Create a WebDriver Chrome instance.
driver = webdriver.Chrome()


#This function `get_player_links` attempts to get the player links from the current page.
# It has an argument `retries` which determines how many times it should retry in case of an exception.
# It returns a list of href attributes for each player link on the page.
def get_player_links(retries=5):
    for i in range(retries):
        try:
            player_divs = driver.find_elements(By.CLASS_NAME, 'text')
            player_links = []
            for player_div in player_divs:
                player_link = player_div.find_element(By.TAG_NAME, 'a')
                player_links.append(player_link)
            return [link.get_attribute('href') for link in player_links]
        except StaleElementReferenceException:
            if i < retries - 1:  # i is zero indexed
                time.sleep(0.5)
                # wait for 2 seconds before trying again
                continue
            else:
                raise
        except NoSuchElementException:
            if i < retries - 1:  # i is zero indexed
                time.sleep(0.5)  # wait for 2 seconds before trying again
                continue
            else:
                raise
        finally:
            print(i)

# `get_urls` function navigates to a specified URL, waits until certain elements are loaded,
# then retrieves and returns the player links on that page using `get_player_links` function.
def get_urls(URL):

    driver.get(URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'player-table-body')))
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))

    return get_player_links(retries=100)          




# Initialize an empty list to store all the player data.
player_list = []

# The loop will iterate over the pages until PAGE_NUM is less than 4500.
while PAGE_NUM < 4500:
    # Get the player URLs from the current page.
    try:
        player_urls = get_urls(URL)

        # For each player URL, it navigates to the player's page, 
        # extracts and parses the HTML, collects the player data, and appends it to `player_list`.
        for player_url in player_urls:

            try:
                # Navigate to the player's page
                driver.get(player_url)


                # Extract the page's HTML
                page_html = driver.page_source

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(page_html, 'html.parser')

                tbl = soup.find('div', class_='row row-cols-2')
                titles = [title.text.strip().replace(' ', '_') for title in tbl.find_all('strong', class_='ttl')]
                text = [txt.text.strip() for txt in tbl.find_all('span', class_='txt')]
                table_dict = dict(zip(titles, text))
                table_dict['Age'] = table_dict['Age'][0:2] if 'Age' in titles else 0
                table_dict['Height'] = table_dict['Height'][0:3] if 'Height' in titles else 0
                table_dict['Weight'] = table_dict['Weight'][0:3].strip() if 'Weight' in titles else 0


                table_dict.pop('xTV_Range')

                trophies_div = soup.find('div', id='playerTrophies')
                
                if trophies_div == None:
                    trophies_list = []
                else:
                    trophies_list = trophies_div.find_all('li')

                xtv_div = soup.find('div', class_='d-row d-val d-flex')
                xtv = xtv_div.find('span', class_='player-tag').text

                value_div = soup.find('div', class_='player-value player-value-large')
                value = value_div.find('span', class_='player-tag').text

                skill = soup.find('div', class_='teamInfoTop-skill__skill')
                skill = str(0.0) if skill == None else skill.text
                pot = soup.find('div', class_='teamInfoTop-skill__pot')
                pot = str(0.0) if pot == None else pot.text

                player = Player(**table_dict,
                                Name=soup.find('a', class_='text-white').text.strip(),
                                Current_Fee=str(value.replace("€", "")),
                                Highest_xTV=str(xtv.replace("€", "")),
                                num_trophies=len(trophies_list),
                                Skill=float(re.findall(r"[-+]?\d*\.\d+|\d+", skill)[0]),
                                Pot= float(re.findall(r"[-+]?\d*\.\d+|\d+", pot)[0]))

                stats = driver.find_element(By.XPATH, '//*[@title="Stats"]')
                if stats == None:
                    continue
                else:
                    stats.click()

                page_html = driver.page_source
                soup = BeautifulSoup(page_html, 'html.parser')

                stats_data = []
                rows = soup.find_all('tr', class_='season-row')

                for row in rows:
                    td_elements = row.find_all('td')
                    row_data = [td.text.strip() for td in td_elements]
                    if row_data[0] == '2022/2023':
                        stats_data.append(row_data)

                if stats_data == []:
                    continue
                
                stats_data = [stats_data[i] for i in range(1, len(stats_data), 2)]
                
                player.Season = stats_data[0][0]
                player.Matches_played = 0 if stats_data[0][1] == '-' else int(stats_data[0][1].strip())
                player.Minutes_played = 0.0 if stats_data[0][2] == '-' else float(stats_data[0][2].strip())
                player.Goals = 0 if stats_data[0][3] == '-' else int(stats_data[0][3].strip())
                player.Assists = 0 if stats_data[0][4] == '-' else int(stats_data[0][4].strip())
                player.Yellow_Cards = 0 if stats_data[0][5] == '-' else int(stats_data[0][5].strip())
                player.Red_Cards = 0 if stats_data[0][6] == '-' else int(stats_data[0][6].strip())
                player.Shots = 0.0 if stats_data[1][3] == '-' else float(stats_data[1][3].strip())
                player.Penalties = 0 if stats_data[1][4] == '-' else int(stats_data[1][4].strip())
                player.Expected_Goals = 0 if stats_data[1][5] == '-' else int(stats_data[1][5].strip())
                player.Attacking_Challenges = 0 if stats_data[1][6] == '-' else float(stats_data[1][6].strip())
                player.Passes = 0 if stats_data[2][3] == '-' else float(stats_data[2][3].strip()) 
                player.Key_Passes = 0 if stats_data[2][4] == '-' else int(stats_data[2][4].strip())
                player.Crosses = 0 if stats_data[2][5] == '-' else int(stats_data[2][5].strip())
                player.Offsides = 0 if stats_data[3][3] == '-' else int(stats_data[3][3].strip())
                player.Ball_Recoveries = 0 if stats_data[3][4] == '-' else int(stats_data[3][4].strip())
                player.Ball_Recoveries_Opponent = 0 if stats_data[3][5] == '-' else int(stats_data[3][5].strip())
                player.Challenges = 0 if stats_data[3][6] == '-' else float(stats_data[3][6].strip())
                player.Air_Challenges = 0 if stats_data[3][7] == '-' else int(stats_data[3][7].strip())
                player.Tackles = 0 if stats_data[3][8] == '-' else int(stats_data[3][8].strip())
                player.Ball_Interceptions = 0 if stats_data[3][9] == '-' else int(stats_data[3][9].strip())
                player.Lost_Balls = 0 if stats_data[4][3] == '-' else int(stats_data[4][3].strip())
                player.Lost_Balls_Own = 0 if stats_data[4][4] == '-' else int(stats_data[4][4].strip())
                player.Errors_to_Goal = 0 if stats_data[4][5] == '-' else int(stats_data[4][5].strip())

                print(player)
                

                player_list.append(player)

            # Handle exceptions during player data collection
            except WebDriverException:
                print(f"WebDriverException occurred. Current URL: {player_url}")
                continue  # or continue if you want to skip to the next URL
            except Exception as e:
                print(e)
                continue
    # Handle exceptions during player URL collection
    except Exception as e:
        PAGE_NUM += 1
        print(f'Page Number: {PAGE_NUM}')
        if not URL[-1].isdigit():
            URL = URL + '/' + str(PAGE_NUM)
        else:
            URL = 'https://www.footballtransfers.com/en/players'
            URL = URL + '/' + str(PAGE_NUM)
        continue  
    # Move on to the next page.
    PAGE_NUM += 1
    print(f'Page Number: {PAGE_NUM}')
    if not URL[-1].isdigit():
        URL = URL + '/' + str(PAGE_NUM)
    else:
        URL = 'https://www.footballtransfers.com/en/players'
        URL = URL + '/' + str(PAGE_NUM)  

# Convert the player data into a dataframe and save it to a CSV file.
player_list = [asdict(player) for player in player_list if type(player) != dict]

df = pd.DataFrame(player_list)
df.to_csv('player_data.csv')

# Quit the driver after finishing all tasks.
driver.quit()
    

