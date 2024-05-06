# This searches the dratings website for MLB matches where dratings thinks a team has a chance of 70% or higher to win

import requests
from bs4 import BeautifulSoup

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
            if table:
                # Now loop through rows of the table
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    team_names = []  # List to store team names in a match
                    green_values = []  # List to store values associated with the teams
                    
                    # Runs through the row to find the 2 team names
                    for cell in cells:
                        if cell.get("class") == ["ta--left", "tf--body"]:
                            # Within each of these td elements, find the span elements
                            span_elements = cell.find_all("span", class_="table-cell--mw d--ib lh--12")
                            for span in span_elements:
                                team_names.append(span.text.strip())  # Add team name to the list
                        
                                
                    # Find the td elements with class "table-division"
                    for cell in cells:
                        if cell.get("class") == ["table-division"]:
                            # Within each of these td elements, find the span elements
                            green_value = cell.find("span", class_="tc--green")
                            if green_value:
                                green_value = green_value.text.strip().replace('%', '')  # Remove percentage sign
                                green_value = float(green_value)  # Convert to float
                                if green_value >= 70:
                                    green_values.append(green_value)

                        
                                    
                    # Associate team names with values if at least one team has a confidence value above 70%
                    if len(team_names) == 2 and len(green_values) > 0:
                        #teams_data.append({team_names[0]: green_values[0], team_names[1]: green_values[0]})
                        teams_data.append({"team_name_1": team_names[0], "team_name_2": team_names[1], "green_value": green_values[0]})
                                
        else:
            print("Parent div with ID 'scroll-completed' not found.")
        
        return teams_data
    else:
        print("Failed to fetch predictions")

if __name__ == "__main__":
    sport_url = "https://www.dratings.com/predictor/mlb-baseball-predictions/"
    # Define the URL for the first page
    page_number = 1
    max_pages = 5  # Maximum number of pages to fetch predictions from
    
    while page_number <= max_pages:
        url = "{}completed/{}#scroll-completed".format(sport_url, page_number)
        predictions = get_predictions(url)
        if predictions:
            print("\n Predictions with confidence score > 70% for page {}:".format(page_number))
            for prediction in predictions:
                
                print("- {} vs {}: {}%".format(prediction['team_name_1'], prediction['team_name_2'], prediction['green_value']))
            page_number += 1

        else:
            print("No more predictions found or none above 70% confidence score.")
            page_number += 1
