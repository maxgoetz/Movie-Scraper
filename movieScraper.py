from bs4 import BeautifulSoup
import re
import schedule
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scopes = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\13366\\Downloads\\Summer Projects\\secret_key_for_movies.json", scopes)
file = gspread.authorize(credentials)
workbook = file.open("Eye Candy")
sheet = workbook.sheet1


def find_movies(): 
    html_text = requests.get("https://www.flixster.com/opening-this-week").text
    soup = BeautifulSoup(html_text, 'lxml')
    movie_container = soup.find('ul', class_="css-10ued2p-UlMovieList e1rfit660")
    movies = movie_container.find_all("li")
    columns = sheet.row_values(1)
    sheet.clear()
    sheet.insert_row(columns, 1)
    for movie in movies:
        if has_score(movie):
            try:
                rating = (movie.find("span", class_ = "css-11czaeu-SpanPercent efkubup0").text.strip())
                half = movie.find("a", class_ = "focus-item__movie-tile")['href']
                href = ("https://www.flixster.com/" + half)
                find_details(href, rating)
            except:
                break



def update_sheet(href, rating, title, description_list, summary):
    body = [href, title, rating, description_list[0], description_list[1], description_list[2], summary]
    sheet.append_row(body, table_range="A2:G2")


def has_score(movie):
    try:
        rating = (movie.find("span", class_ = "css-11czaeu-SpanPercent efkubup0").text.strip())
        if len(rating) < 5:
            return True
    except:
        return
    

def fix_formatting(description):
    rating_pattern = r'(R|PG-13|PG|G)'
    duration_pattern = r'(\d+ hr \d+ min|\d+ hr|\d+ min)'
    date_pattern = r'([A-Z][a-zA-Z]* \d{1,2}, \d{4})'

    rating_match = re.search(rating_pattern, description)
    duration_match = re.search(duration_pattern, description)
    date_match = re.search(date_pattern, description)

    rating = rating_match.group() if rating_match else ""
    duration = duration_match.group(1) if duration_match else ""
    release_date = date_match.group() if date_match else "" 

    if rating == "PG-13":
        duration = duration[2:]

    return [rating, duration, release_date]


def find_details(href, rating):
    link = requests.get(href).text
    soup = BeautifulSoup(link, 'lxml')
    try:
        title = (soup.find("h1", class_ = "h1 css-1r46kl3-H1Title egdh09h2").text.strip())
        description = (soup.find("div", class_ = "css-nwptni-PMetaData egdh09h3").text.strip())
        description_list = fix_formatting(description)
        summary = (soup.find("div", class_ = "LinesEllipsis").text.strip())
        update_sheet(href, rating, title, description_list, summary)
    except:
        return  
    

schedule.every().tuesday.at("06:00").do(find_movies)

while True:
    schedule.run_pending()
    time.sleep(1800)