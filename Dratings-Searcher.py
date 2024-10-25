import requests
from bs4 import BeautifulSoup
import statistics
import math

# Converts American odds to decimal
def american_to_decimal(american_odds):
    if american_odds > 0:
        return round((american_odds / 100) + 1, 2)
    elif american_odds < 0:
        return round((100 / abs(american_odds)) + 1, 2)
    else:
        return 1.00  # If American odds are 0, return decimal odds of 1.00

# Checks if dratings probability is 5% more than the bookies 
def isValueBet(current_odds, dratings_probability):
    bookies_probability = round((1/current_odds)*100, 1)
    if dratings_probability > bookies_probability + 5:
        return True
    return False

# Calculates the profit for a value bet
def valueBetCalculator(current_odds, dratings_probability):
    value_bets_profit = 0
    bookies_probability = round((1/current_odds)*100, 1)
    
    if dratings_probability > bookies_probability + 5:
        if prediction['win_or_lose'] == "Win":
            value_bets_profit += (prediction['odds']-1)
        if prediction['win_or_lose'] == "Loss":
            value_bets_profit -= 1
            
    return value_bets_profit

# Get team name
def getTeamName(new_row, team_position):
    for cell in new_row:
        if cell.get("class") == ["ta--left", "tf--body"]:
            spany_elements = cell.find_all("span", class_="table-cell--mw d--ib lh--12")
            team_name = spany_elements[team_position].text
            
    return team_name

# Determines if chosen team has lost or won
def matchOutcome(chosen_sport, new_row, team_position):
    point_sports = ["NBA", "NFL", "NHL", "MLB", "NCAA", "Champions", "Premier"]
    if chosen_sport == "UFC":
        for cell in new_row:
            if cell.text == "WinLoss" and team_position == 0:
                win_or_lose = cell.text.strip("Loss")
            elif cell.text == "WinLoss" and team_position == 1:
                win_or_lose = cell.text.strip("Win")
            elif cell.text == "LossWin" and team_position == 0:
                win_or_lose = cell.text.strip("Win")
            elif cell.text == "LossWin" and team_position == 1:
                win_or_lose = cell.text.strip("Loss")
        
    elif chosen_sport in point_sports:
        points = new_row[5]
        numbers = points.get_text(separator=" ").split()  # Splitting based on white space separator
        
        # Assign the numbers to separate variables
        first_teams_points = int(numbers[0])
        second_teams_points = int(numbers[1])
        
        if team_position == 0 and first_teams_points > second_teams_points:
            win_or_lose = "Win"
        elif team_position == 1 and first_teams_points < second_teams_points:
            win_or_lose = "Win"
        else:
            win_or_lose = "Loss"

    return win_or_lose

# Get odds
def getOdds(row, colour):
    vegas_sportsbook_div = row.find('div', class_='vegas-sportsbook')
    if vegas_sportsbook_div:
        odd = vegas_sportsbook_div.text.strip()
        dash_count = odd.count("-")
        plus_count = odd.count("+")

        # If both are fave/underdog
        if dash_count>=2 or plus_count>=2:
            odd = "100"
        elif not odd:
            odd = 0
        # If first odd is favorite 
        elif odd[0] == '-':
            if colour == "green":
                odd = odd.split('+')[0]
            elif colour == "red":
                odd = odd.split('+')[1]
        # If first odd is underdog
        elif odd[0] == '+':
            if colour == "green":
                odd = odd.split('-')[1]
                odd = "-" + odd
            elif colour == "red":
                odd = odd.split('-')[0]
        else:
            odd = odd.split('-')[1]
            odd = "-" + odd

        odd = int(odd)
        decimal_odd = american_to_decimal(odd)

    return decimal_odd

def get_predictions(chosen_sport, url):
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
                    new_row = row.find_all("td") # For each row in the table, convert its format
                    team_position = -1
                    win_or_lose = ""
                    
                    # Loop through each cell in a row
                    for cell in new_row:
                        if cell.get("class") == ["table-division"]:  # Filter for confidence
                            # Within each of these td elements, find the span elements
                            span_elements = cell.find_all("span", class_=True)
                            
                            # Finds if the team with a green confidence score is first or second visually
                            if span_elements:
                                first_class = span_elements[0]['class'][0]
                                if first_class == "tc--green": # Team is visually first (top)
                                    team_position = 0
                                elif first_class == 'tc--red': # Team is visually second (bottom)
                                    team_position = 1

                                         
                                # Now that we know which team is green and red, find the confidence score of green team
                                green_value = cell.find("span", class_="tc--green")
                                if green_value:
                                    green_value = green_value.text.strip().replace('%', '')  # Remove percentage sign
                                    green_value = float(green_value)  # Convert to float

                                    # Now filter out teams that don't have a high confidence score
                                    if green_value >= 0:
                                        # Checks if green team won or lost, their name and their odds
                                        match_outcome = matchOutcome(chosen_sport, new_row, team_position)
                                        team_name = getTeamName(new_row, team_position)
                                        decimal_odd = getOdds(row, "green")

                                        teams_data.append({"fighter_name": team_name, 
                                                           "green_value": green_value, 
                                                           "odds": decimal_odd, 
                                                           "win_or_lose": match_outcome})

                                        
                                
        else:
            print("Parent div with ID 'scroll-completed' not found.")
        
        return teams_data
    else:
        print("Failed to fetch predictions")


if __name__ == "__main__":
    sports_list = {"UFC": "https://www.dratings.com/predictor/ufc-mma-predictions/", 
                   "NBA": "https://www.dratings.com/predictor/nba-basketball-predictions/", 
                   "NFL": "https://www.dratings.com/predictor/nfl-football-predictions/",
                   "NHL": "https://www.dratings.com/predictor/nhl-hockey-predictions/",
                   "MLB": "https://www.dratings.com/predictor/mlb-baseball-predictions/", 
                   "NCAA": "https://www.dratings.com/predictor/ncaa-basketball-predictions/",
                   "Champions": "https://www.dratings.com/predictor/champions-league-predictions/"
                  }
    conference_sport_list = {"Premier": "https://www.dratings.com/predictor/english-premier-league-predictions/"}

    # Merge all sports into one dictionary
    all_sports = {**sports_list, **conference_sport_list}
    # Set for quick lookup of sports in conference_sport_list
    conference_sports = set(conference_sport_list.keys())

    print("Available sports:")
    for sport in all_sports:
        print(f"- {sport}")

    is_sport_chosen = False
    while is_sport_chosen == False:
        chosen_sport = input("Pick a sport:")
        if chosen_sport in all_sports:
            sports_url = all_sports[chosen_sport]
            is_sport_chosen = True
        else:
            print("Sport unrecognised. Enter again")
        
    # Define the URL for the first page
    page_number = 1
    max_pages = 7  # Maximum number of pages to fetch predictions from
    total_odds = []
    total_wins_counter = 0
    total_bets_counter = 0
    betting_count = 0 # Counts current profit n loss

    value_bets_profit = 0
    total_value_bets_counter = 0
    
    while page_number <= max_pages:
        # Loads URL depending on type of sport
        if chosen_sport in conference_sports:
            url = "{}completed/{}?conference_id=55#scroll-completed".format(sports_url, page_number)
        else:
            url = "{}completed/{}#scroll-completed".format(sports_url, page_number)

        # Get predictions
        predictions = get_predictions(chosen_sport, url)

        if predictions:
            print("\nPredictions with confidence score > 70% for page {}:".format(page_number))
            for prediction in predictions:
                if prediction['win_or_lose'] == "Win":
                  total_wins_counter += 1
                  total_bets_counter += 1
                  betting_count += (prediction['odds']-1)
                    
                else:
                  total_bets_counter += 1
                  betting_count -= 1

                # Value bets section
                if isValueBet(prediction["odds"], prediction["green_value"]):
                    total_value_bets_counter += 1
                    value_bets_profit += valueBetCalculator(prediction["odds"], prediction["green_value"])
                    print("{}, {}%, {}, {}, {}".format(prediction['fighter_name'], prediction['green_value'], prediction['win_or_lose'], prediction["odds"], "VALUE"))
                else:       
                    print("{}, {}%, {}, {}".format(prediction['fighter_name'], prediction['green_value'], prediction['win_or_lose'], prediction["odds"]))
                    
                total_odds.append(prediction['odds'])
            page_number += 1
        else:
            print("No more predictions found or none above 70% confidence score.")
            page_number += 1

    if total_odds:
        mean_odds = statistics.mean(total_odds)
        win_rate = total_wins_counter/total_bets_counter
        print("\n \nAverage Odds: ", math.floor(mean_odds * 100) / 100)
        print("Total profit", math.floor(betting_count * 100) / 100, "/", total_bets_counter, "=", math.floor(betting_count / total_bets_counter * 100), "%")
        
    else:
        print("\n \nAverage Odds: 0")
        print("Total profit: 0")
        
        
    print(f"Win rate: {total_wins_counter} / {total_bets_counter} = {win_rate}")
    if total_value_bets_counter != 0:
        print(f"Value bets profit", math.floor(value_bets_profit * 100) / 100, "/", total_value_bets_counter, "=", math.floor(value_bets_profit / total_value_bets_counter * 100), "%")
        
    else: print("Value bets profit: 0/0")

# UFC 0%+ confidence value bets give 42% profit (2.94/7)
