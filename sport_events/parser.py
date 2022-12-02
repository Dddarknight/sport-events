from time import sleep
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from sport_events.database import migrate


URL = "https://www.sofascore.com/"


class Ids(Enum):
    MENU = 'downshift-2-menu'


class Attrs(Enum):
    LINK = 'href'


class Classes(Enum):
    SPORT_NAME = 'sportName'
    SPORT_NAME_IN_MENU = 'hoqAOw'
    EVENT = 'bRnoMe'
    COUNTRY = 'hFdMbf'
    TOURNAMENT = 'cFDHvI'
    COMPETITORS = 'eIlfTT'
    TIME = 'kafPPN'
    LIVE = 'iYMA-DU'
    NOTLIVE = 'JMbdj'


class Tags(Enum):
    URL = 'a'
    DIV = 'div'


class Parser:
    driver = webdriver.Firefox()
    url = URL
    sports = {}

    def get_sports(self):
        self.driver.get(self.url)
        for link in self.driver.find_elements(By.TAG_NAME, Tags.URL.value):
            try:
                sport = link.find_element(
                    By.CLASS_NAME, Classes.SPORT_NAME.value)
            except Exception:
                sport = ''
            if sport:
                self.sports[sport.text] = {
                    'link': link.get_attribute(Attrs.LINK.value)
                }
        menu = self.driver.find_element(
            By.ID, Ids.MENU.value
        )
        links = menu.find_elements(
            By.TAG_NAME, Tags.URL.value
        )
        sleep(1)
        for link in links:
            sport = link.find_element(
                By.CLASS_NAME, Classes.SPORT_NAME_IN_MENU.value)
            if sport:
                sport_name = sport.get_attribute("textContent")
                self.sports[sport_name] = {
                    'link': link.get_attribute(Attrs.LINK.value)
                }

    def migrate_sports(self):
        for sport_name, sport_link in self.sports.items():
            if sport_name:
                self.driver.get(sport_link['link'])
                all_competitors = set()
                try:
                    self.driver.find_element(
                        By.CLASS_NAME, Classes.LIVE.value).click()
                    live_events_output, all_competitors = self.get_events()
                    self.sports[sport_name].update({
                        'events': live_events_output
                    })
                except Exception:
                    pass
                try:
                    self.driver.find_element(
                        By.CLASS_NAME, Classes.NOTLIVE.value).click()
                    not_live_events_output, _ = self.get_events(
                        category='NotLive', all_competitors=all_competitors)
                    if all_competitors:
                        self.sports[sport_name]['events'].extend(
                            not_live_events_output
                        )
                    else:
                        self.sports[sport_name].update({
                            'events': not_live_events_output
                        })
                except Exception:
                    pass
                sleep(1)
        migrate(self.sports)

    def get_events(self, category='Live', all_competitors=set()):
        try:
            events = wait(self.driver, 10).until(
                EC.visibility_of_all_elements_located(
                    (By.CLASS_NAME, Classes.EVENT.value))
            )
        except Exception:
            return [], set()
        sleep(1)
        events_output = []
        for event in events:
            try:
                time = event.find_element(
                    By.CLASS_NAME, Classes.TIME.value).text
            except Exception:
                continue
            try:
                competitors_elements = event.find_element(
                    By.CLASS_NAME, Classes.COMPETITORS.value).find_elements(
                        By.TAG_NAME, Tags.DIV.value)
                competitors = [
                    element.text for element in competitors_elements
                ]
            except Exception:
                competitors = ['', '']
            if tuple(competitors) in all_competitors:
                continue
            all_competitors.add(tuple(competitors))
            events_output.append({
                    'competitors': competitors,
                    'time': time,
                    'category': category,
            })
            sleep(1)
        return events_output, all_competitors
