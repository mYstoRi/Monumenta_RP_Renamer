import requests
import json

url = 'https://api.playmonumenta.com/items'


def get_api():
    print('fetching from api...')
    response = requests.get(url)
    if response.status_code == 200:
        d = response.json()
        print('finished fetching from api.')
        return d
    print(f"Error {response.status_code}: {response.text}")
    return None


data = get_api()

if __name__ == '__main__':
    print(data['Polished Jade'])
