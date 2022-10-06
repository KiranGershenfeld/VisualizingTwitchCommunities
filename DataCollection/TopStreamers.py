from urllib.error import HTTPError
import requests
import math

NUM_CHANNELS = 1000

def lambda_handler(event, context):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    steps = math.ceil(NUM_CHANNELS / 100.0)

    channel_list = []
    for step in range(steps):
        start_index = step * 100

        try:
            request = requests.get(f'https://sullygnome.com/api/tables/channeltables/getchannels/7/0/0/3/desc/{start_index}/100', headers=headers)
        except HTTPError as e:
            print(e)
            return

        if(request.status_code == 200):
            data = request.json()['data']
            channels = [channel['url'] for channel in data]
            channel_list.extend(channels)
        else:
            print(f"Response returned with status code: {request.status_code}")

    channel_list = channel_list[0: NUM_CHANNELS]
    return channel_list

if __name__ == '__main__':
    lambda_handler(None, None)