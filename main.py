import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def collect_movie_data():
    movie_data = {
        "timestamp": input("Enter date of watching (YYYY-MM-DD): "),
        "movie_name": input("Enter movie name: "),
        "movie_release_year": input("Enter movie release year (YYYY): "),
        "user_rating": input("Enter your rating of the movie (X.X): "),
        "first_time": input("Is this the first time watching it? (yes/no): ")    
    }
    return movie_data

def store_in_csv(movie_data):
    with open('movies.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            movie_data["timestamp"], 
            movie_data["movie_name"],
            movie_data["movie_release_year"],
            movie_data["user_rating"], 
            movie_data["first_time"]
        ])
    print("Movie added successfully!")

def get_imdb_data(imdb_url):
    response = requests.get(imdb_url)
    soup = BeautifulSoup(response.text, 'html.parser')    

    title = soup.find('h1').text.strip()
    print("movie title:", {title})
    year = soup.find('span', {'id': 'titleYear'}).a.text.strip()
    return title, year


def update_year_markdown():
    movies = []

    with open('movies.csv', newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            timestamp, movie_name, movie_release_year, user_rating, first_time = row
            movies.append([timestamp, movie_name, movie_release_year, user_rating, first_time])

    with open('yearly_movies.md', 'w') as md_file:
        md_file.write("| # | Date of Watching | Title | Year of Release | My Rating | First Time? |\n")
        md_file.write("|---|------------------|-------|-----------------|-----------|-------------|\n")

        for index, movie in enumerate(movies, start=1):
            md_file.write(f"| {index} | {movie[0]} | {movie[1]} | {movie[2]} | {movie[3]} | {'X' if movie[4].lower() == 'yes' else ' '} |\n")

    print("yearly markdown file updated!")


def update_overview():
    movies_by_year = {}

    # Read the CSV data
    with open('movies.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            timestamp, movie_name, movie_release_year, user_rating, first_time = row
            watch_year = datetime.strptime(timestamp, '%Y-%m-%d').year

            if watch_year not in movies_by_year:
                movies_by_year[watch_year] = []

            movies_by_year[watch_year].append({
                'release_year': int(movie_release_year),
                'rating': float(user_rating),
                'first_time': first_time.lower() == 'yes'
            })

    # Calculate summary statistics
    overview = {}
    for year, movies in movies_by_year.items():
        ratings = [movie['rating'] for movie in movies]
        release_years = [movie['release_year'] for movie in movies]
        first_time_count = sum(movie['first_time'] for movie in movies)

        overview[year] = {
            'avg_rating': sum(ratings) / len(ratings),
            'avg_release_year': sum(release_years) / len(release_years),
            'median_release_year': sorted(release_years)[len(release_years) // 2],
            'oldest_release_year': min(release_years),
            'newest_release_year': max(release_years),
            'percent_first_time': (first_time_count / len(movies)) * 100,
        }

    # Write the overview to markdown
    with open('overview.md', 'w') as md_file:
        md_file.write("| Year | Avg Rating | Avg Release Year | Median Release Year | Oldest | Newest | % First Time |\n")
        md_file.write("|------|------------|------------------|---------------------|--------|--------|--------------|\n")

        for year, stats in overview.items():
            md_file.write(f"| {year} | {stats['avg_rating']:.2f} | {stats['avg_release_year']:.0f} | {stats['median_release_year']} | "
                          f"{stats['oldest_release_year']} | {stats['newest_release_year']} | {stats['percent_first_time']:.2f}% |\n")

    print("Overview markdown file updated!")


def main():
    new_movie_entry = collect_movie_data()

    store_in_csv(new_movie_entry)
    update_year_markdown()
    update_overview()
    
if __name__ == "__main__":
    main()
