from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from tempfile import mkdtemp
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import telebot


def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome("/opt/chromedriver",
                            options=options)
    # Telegram Bot API token
    BOT_TOKEN = '6542414604:AAHc3LpkR5Ukxfy-TwAJgd27MvuH6FED-q8'
    bot = telebot.TeleBot(BOT_TOKEN)

    movie_cinemas = {}

    driver.get('https://www.gv.com.sg/')  # Replace this with the actual URL

    # Wait for the page to load (You may need to add explicit wait here if the page has dynamic content)
    wait = WebDriverWait(driver, 10)

    page_content = driver.page_source

    soup = BeautifulSoup(page_content, 'html.parser')

    # Find all the movie entries
    movie_entries = soup.find_all('div', class_='col-xs-4 col-sm-3 col-md-2 ng-scope')

    def scrape_movie_data(movie_entries):
        movie_data = {}
        for entry in movie_entries:
            # Extract the movie name from the 'h5' tag
            movie_name_tag = entry.find('h5', class_='ng-binding')
            if movie_name_tag:
                movie_name = movie_name_tag.get_text().strip()
                # Remove the asterisk (*) from the movie title
                movie_name = movie_name.replace('*', '').strip()
            else:
                continue

            # Find the 'img' tag
            img_tag = entry.find('img')
            if img_tag:
                # Extract the ng-src attribute value
                ng_src_value = img_tag['ng-src']
                # Use regex to find the numeric part after 'img'
                numeric_part = re.search(r'img(\d+)\.jpg', ng_src_value)
                if numeric_part:
                    numeric_part = numeric_part.group(1)
                    # Store unique movie title and numeric part in the dictionary (using lowercase movie_name as the key)
                    movie_data[movie_name.lower()] = numeric_part

        return movie_data

    movie_data = scrape_movie_data(movie_entries)

    # Quit the driver after scraping movie data
    driver.quit()
        
    def get_available_cinemas(selected_movie, movie_entries):
        
        driver = webdriver.Chrome("/opt/chromedriver",
                            options=options)
        
        cinemas = []
        cinema_timings = {}

        wait = WebDriverWait(driver, 10)

        for entry in movie_entries:
            movie_name_tag = entry.find('h5', class_='ng-binding')

            if movie_name_tag:
                movie_name = movie_name_tag.get_text().strip()
                movie_name = movie_name.replace('*', '').strip()
                if movie_name.lower() == selected_movie.lower():
                    img_tag = entry.find('img')
                    if img_tag:
                        ng_src_value = img_tag['ng-src']
                        numeric_part = re.search(r'img(\d+)\.jpg', ng_src_value)
                        if numeric_part:
                            numeric_part = numeric_part.group(1)
                            website_redirect = f'https://www.gv.com.sg/GVMovieDetails?movie={numeric_part}#/movie/{numeric_part}'
                            try:
                                driver.get(website_redirect)
                                wait = WebDriverWait(driver, 10)
                            except Exception as e:
                                print(f"Error: {e}")
                            
                            cinema_elements = driver.find_elements(By.XPATH, "//li[@ng-repeat='cinema in cinemaList']")
                            for cinema_element in cinema_elements:
                                cinema_name = cinema_element.text.strip()
                                cinemas.append(cinema_name)
                                try:
                                    cinema_element.click()
                                except Exception:
                                    # If clicking the element fails, use JavaScript to click it
                                    driver.execute_script("arguments[0].click();", cinema_element)

                                # Wait for the timings container to be loaded for the selected cinema
                                timings_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-unstyled')))

                                # Find all the list items (li) inside the timings container, representing each day's schedule
                                days_elements = timings_container.find_elements(By.XPATH, "//li[@ng-repeat='timeslot in selectedCinema.timeslots']")
                                
                                # Create a dictionary to store timings for each day
                                timings_for_cinema = {}

                                for day_element in days_elements:
                                    # Extract the day from the 'span' tag
                                    day_tag = day_element.find_element(By.CLASS_NAME, 'day')
                                    date_tag = day_element.find_element(By.CLASS_NAME, 'date')
                                    day = day_tag.text.strip()
                                    date = date_tag.get_attribute("textContent").strip()

                                    # Find all the button elements inside the current day's schedule
                                    button_elements = day_element.find_elements(By.XPATH, ".//button[contains(@class, 'btn-primary')]")

                                    timings_for_day = []
                                    for button in button_elements:
                                        timing = button.get_attribute("textContent").strip()
                                        timings_for_day.append(timing)

                                    timings_for_cinema[day] = {"date": date, "timings": timings_for_day}

                                cinema_timings[cinema_name] = timings_for_cinema

                            # Quit the driver after all cinema locations are processed
                            driver.quit()

        return (cinemas, cinema_timings)


    # Telegram bot handler
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        movie_buttons = []
        for movie_name in movie_data:
            movie_buttons.append(telebot.types.KeyboardButton(movie_name.capitalize()))
        markup.add(*movie_buttons)
        bot.send_message(message.chat.id, "Welcome to MovieBot! Please select a movie:", reply_markup=markup)


    # New: Handle user movie selection and display cinema buttons
    @bot.message_handler(func=lambda message: message.text.lower() in movie_data)
    def handle_movie_selection(message):
        selected_movie = message.text.lower()
        available_cinemas, cinema_timings = get_available_cinemas(selected_movie, movie_entries)
        if available_cinemas:
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            cinema_buttons = []
            for cinema_name in available_cinemas:
                cinema_buttons.append(telebot.types.KeyboardButton(cinema_name))
            markup.add(*cinema_buttons)
            bot.send_message(message.chat.id, f"Select a cinema for {selected_movie.capitalize()}:", reply_markup=markup)
            
            # Store the available cinemas and timings for the selected movie
            movie_cinemas[message.chat.id] = (selected_movie, available_cinemas, cinema_timings)
        else:
            bot.send_message(message.chat.id, "No cinemas available for the selected movie.")

    # New: Handle user cinema selection and display timings
    @bot.message_handler(func=lambda message: message.text in movie_cinemas.get(message.chat.id, ([], {}))[1])
    def handle_cinema_selection(message):
        selected_cinema = message.text
        selected_movie, _, cinema_timings = movie_cinemas.get(message.chat.id, (None, None, {}))
        if selected_movie and selected_cinema:
            timings = cinema_timings[selected_cinema]
            
            # Create an inline keyboard with buttons for each day's timings
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            for day, data in timings.items():
                timings_button = telebot.types.InlineKeyboardButton(
                    text=f"{day} {data['date']}", callback_data=f"{selected_movie} {selected_cinema} {day}_{data['date']}"
                )

                markup.add(timings_button)
            
            bot.send_message(
                message.chat.id,
                f"Timings for {selected_movie.capitalize()} at {selected_cinema}:\nSelect a day:",
                reply_markup=markup,
            )
        else:
            bot.send_message(message.chat.id, "Invalid selection.")

    # New: Handle user callback query for timings
    @bot.callback_query_handler(func=lambda call: True)
    def handle_timings_callback(call):
        bot.answer_callback_query(call.id, text="Timings information is displayed above.")

    # Help command handler
    @bot.message_handler(commands=['help'])
    def handle_help(message):
        help_message = (
            "Welcome to MovieBot!\n"
            "To start over and see the list of available movies, simply type /start."
        )
        bot.send_message(message.chat.id, help_message)


    # Start the Telegram bot
    bot.polling()


