import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import csv

class FlightTracker:
    def __init__(self, db_name='flights.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flight_number TEXT,
                    status TEXT,
                    airport TEXT,
                    delay INTEGER
                )
            ''')

    def fetch_flight_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to retrieve data from {url}")

    def parse_flight_data(self, html, airport):
        soup = BeautifulSoup(html, 'html.parser')
        flights = []
        # Предполагается, что данные о рейсах находятся в таблице с определенным классом
        flight_rows = soup.find_all('tr', class_='flight-row')
        
        for row in flight_rows:
            flight_number = row.find('td', class_='flight-number').text
            status = row.find('td', class_='status').text
            delay = self.extract_delay(status)
            flights.append((flight_number, status, airport, delay))
        
        return flights

    def extract_delay(self, status):
        # Пример обработки статуса для извлечения задержки
        if "delayed" in status.lower():
            return int(status.split(' ')[-1])  # Предполагается, что задержка указана в конце
        return 0

    def save_to_database(self, flights):
        with self.conn:
            self.conn.executemany('''
                INSERT INTO flights (flight_number, status, airport, delay)
                VALUES (?, ?, ?, ?)
            ''', flights)

    def export_to_csv(self, airport, csv_file):
        df = pd.read_sql_query(f'SELECT * FROM flights WHERE airport="{airport}"', self.conn)
        df.to_csv(csv_file, index=False)

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    tracker = FlightTracker()
    url = 'https://www.svo.aero/'  # Замените на реальный URL
    airport = 'Example Airport'
    
    html = tracker.fetch_flight_data(url)
    flights = tracker.parse_flight_data(html, airport)
    tracker.save_to_database(flights)
    tracker.export_to_csv(airport, f'{airport}_flights.csv')
    tracker.close()