# UFC version
# 30, 40, 50, 100 pages -> 80%
# 10, 20 pages -> 76%


import requests
from bs4 import BeautifulSoup
import statistics
import math

def american_to_decimal(american_odds):
    if american_odds > 0:
        return round((american_odds / 100) + 1, 2)
    elif american_odds < 0:
        return round((100 / abs(american_odds)) + 1, 2)
    else:
        return 1.00  # If American odds are 0, return decimal odds of 1.00
        
def get_predictions(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        teams_data = []  # List to store team names and associated values
        
        # Find the parent div with ID scroll-completed
        parent_div = soup.find("div", id="scroll-completed")
        
        # Check if the parent div exists
        if parent_div:
            # Find the table within the parent div
            table = parent_div.find("table")
            betting_count = 0
            if table:
                # Now loop through rows of the table
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    fighter_win = []
                    fighter_position = -1
                    win_or_lose = ""
                    
                    
                    for cell in cells:
                        if cell.get("class") == ["table-division"]:  # Filter for confidence
                            # Within each of these td elements, find the span elements
                            span_elements = cell.find_all("span", class_=True)
                            
                            # Find if green confidence is first or second
                            if span_elements:
                                first_class = span_elements[0]['class'][0]
                                if first_class == 'tc--red':
                                    fighter_position = 1
                                    
                                elif first_class == 'tc--green':
                                    fighter_position = 0
                                    
                                # Find the green value
                                green_value = cell.find("span", class_="tc--green")
                                if green_value:
                                    green_value = green_value.text.strip().replace('%', '')  # Remove percentage sign
                                    green_value = float(green_value)  # Convert to float
                                    if green_value >= 70:  # Only find team names and odds if dratings confidence >= 70

                                      # Once green value found, print out fighters name
                                      for cell in cells:
                                        if cell.get("class") == ["ta--left", "tf--body"]:
                                          # Once fighters name found, print their name
                                          spany_elements = cell.find_all("span", class_="table-cell--mw d--ib lh--12")
                                          
                                      # Determines if the fighter won or lost
                                      for cell in cells:
                                        if cell.text == "WinLoss" and fighter_position == 0:
                                            win_or_lose = cell.text.strip("Loss")
                                        elif cell.text == "WinLoss" and fighter_position == 1:
                                            win_or_lose = cell.text.strip("Win")
                                        elif cell.text == "LossWin" and fighter_position == 0:
                                            win_or_lose = cell.text.strip("Win")
                                        elif cell.text == "LossWin" and fighter_position == 1:
                                            win_or_lose = cell.text.strip("Loss")                                          
                                          
                                      
                                      vegas_sportsbook_div = row.find('div', class_='vegas-sportsbook')
                                      if vegas_sportsbook_div:
                                          odd = vegas_sportsbook_div.text.strip()
                                          dash_count = odd.count("-")
                                          
                                          # If both are somehow favourites, just take the first odds value since they're usually around the same
                                          if dash_count>=2:
                                              odd_parts = odd.split('-')
                                              odd = odd_parts[0]
                                          elif not odd:
                                              odd = 0
                                          elif odd[0] == '-':
                                              odd = odd.split('+')[0]
                                          elif odd[0] == '+' and odd[4] == '+': #If both are underdogs 
                                              first_odd = odd.strip()[:4]
                                              second_odd = odd.strip()[4:]
                                              if first_odd >= second_odd:
                                                odd = second_odd
                                              else:
                                                odd = first_odd
                                          else:
                                              odd = odd.split('-')[1]
                                              odd = "-" + odd
                                              
                                          odd = int(odd)
                                          decimal_odd = american_to_decimal(odd)

                                      teams_data.append({"fighter_name": spany_elements[fighter_position].text, 
                                                         "green_value": green_value, 
                                                         "odds": decimal_odd, 
                                                         "win_or_lose": win_or_lose})
                                        
                                
        else:
            print("Parent div with ID 'scroll-completed' not found.")
        
        return teams_data
    else:
        print("Failed to fetch predictions")


# 30, 40, 50, 100 pages -> 80%
# 10, 20 pages -> 76%
if __name__ == "__main__":
    sport_url = "https://www.dratings.com/predictor/ufc-mma-predictions/"
    # Define the URL for the first page
    page_number = 1
    max_pages = 10  # Maximum number of pages to fetch predictions from
    total_odds = []
    total_wins_counter = 0
    total_bets_counter = 0
    betting_count = 0
    
    while page_number <= max_pages:
        url = "{}completed/{}#scroll-completed".format(sport_url, page_number)
        predictions = get_predictions(url)
        if predictions:
            print("\nPredictions with confidence score > 70% for page {}:".format(page_number))
            for prediction in predictions:
                if prediction['win_or_lose'] == "Win":
                  total_wins_counter+=1
                  total_bets_counter+=1
                  betting_count+=(prediction['odds']-1)
                else:
                  total_bets_counter+=1
                  betting_count-=1
                  
                print("{}, {}%, {}, {}".format(prediction['fighter_name'], prediction['green_value'], prediction['win_or_lose'], prediction["odds"]))
                total_odds.append(prediction['odds'])
            page_number += 1
        else:
            print("No more predictions found or none above 70% confidence score.")
            page_number += 1

    mean_odds = statistics.mean(total_odds)
    win_rate = total_wins_counter/total_bets_counter
    print("\nWin rate", total_wins_counter, "/", total_bets_counter, "=", win_rate)
    print("Average Odds: ", math.floor(mean_odds * 100) / 100)
    print("Total profit", math.floor(betting_count * 100) / 100, "/", total_bets_counter, "=", math.floor(betting_count / total_bets_counter * 100) / 100, "%")
