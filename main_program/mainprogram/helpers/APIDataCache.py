import json
import pickle
from tkinter import messagebox
import requests
from datetime import datetime, timedelta

class APIDataCache:
    def __init__(self, cache_filename, cache_expiry_duration=timedelta(days=30)):
        self.cache_filename = cache_filename
        self.cache_expiry_duration = cache_expiry_duration
        self.cache = self._load_cache()
        self.url = "https://rq-www-lr.researchquran.org/api/get-quran-data"


    def _load_cache(self):
        try:
            with open(self.cache_filename, 'rb') as cache_file:
                return pickle.load(cache_file)
        except (FileNotFoundError, pickle.PickleError):
            return {'timestamp': None, 'data': None}

    def _save_cache(self):
        with open(self.cache_filename, 'wb') as cache_file:
            pickle.dump(self.cache, cache_file)

        # json_output = json.dumps(self.cache['data'], ensure_ascii=False, indent=4)
        # with open(f"record_files/sample.json", "w", encoding="utf-8") as json_file:
        #     json_file.write(json_output)

    def _fetch_data_from_api(self):
        try:
            response = requests.get( self.url )
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            self.show_error_message("Error fetching data from API:\n" + str(e))
            return None

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def get_data(self):
        current_time = datetime.now()
        cached_time = self.cache['timestamp']
        cached_data = self.cache['data']

        if cached_data is None or cached_time is None or (current_time - cached_time) >= self.cache_expiry_duration:
            new_data = self._fetch_data_from_api()
            if new_data is not None:
                self.cache['data'] = new_data
                self.cache['timestamp'] = current_time
                self._save_cache()
            return new_data
        else:
            return cached_data

# if __name__ == "__main__":
#     cache = APIDataCache(cache_filename='record_files/data_cache.pkl')
#     data = cache.get_data()

#     if data is not None:
#         print(data)
