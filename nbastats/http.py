import requests

def get_response(url, params):
    """makes a request and returns the string response

    arguments:
        url: a string for the base url.
        params: a dictionary for any queries.

    returns:
        a string of the response decoded based on the encoding format in the 
        returned header.
    """

    response = requests.get(
        url = url,
        params = params,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
    )

    return response.content.decode(response.encoding)