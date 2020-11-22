# Degrees-CS50

### Background
According to the Six Degrees of Kevin Bacon game, anyone in the Hollywood film industry can be connected to Kevin Bacon within six steps,
where each step consists of finding a film that two actors both starred in. In this problem, we’re interested in finding the shortest path
between any two actors by choosing a sequence of movies that connects them. For example, the shortest path between Jennifer Lawrence and Tom Hanks is 2: 
Jennifer Lawrence is connected to Kevin Bacon by both starring in “X-Men: First Class,” and Kevin Bacon is connected to Tom Hanks by both starring in “Apollo 13.”

### Features
This is a flask app which displays the connection between any two actors in Hollywood based on the 
movies they have acted in. There are two main features in the app:

- Connection with images
  - The program scrapes google images and provides images of the actors to the user in the form 
  of a carousel.
  
- Fast connection
  - The program only displays the connection between two actors without images.
  
### How to run app (Windows)
  - Create a git repository and use
    - git clone https://github.com/AloysiusAmbe/Degrees-CS50.git
  - Use 'pip-install -r requirements.txt' to install all the needed depencies
  - cd into the directory where the source code is downloaded and run
    - set FLASK_APP=app.py
    - flask run
    - Copy and paste the local url into your browser

### Note
  - It takes a while for the app to load since all the data is being loaded into memory at that time.
  - Scraping the images from google is a slow process and the scraper downloads the url of the first image from google.

### Acknowledgements
  - All data courtesy of 'Havard's CS50 Introduction to Artificial Intelligence' course on EDx.
