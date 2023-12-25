from requests_oauthlib import OAuth1Session
import json
import requests
from bs4 import BeautifulSoup
import time

consumer_key = 'consumer_keyiniz'
consumer_secret = 'consumer_secretiniz'
access_token='access_tokeniniz'
access_token_secret='access_token_secretiniz'

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

# Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.


# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print("\033[91m", end="")
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )
    print("\033[0m", end="")
    
    exit(1)

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)


sayac=0

while True:
    try:
        def scrape(url, sayac,ar):
            response = requests.get(url)
            time.sleep(1)
            html_icerigi = response.content
            soup = BeautifulSoup(html_icerigi, "html.parser")
            tbody = soup.find("tbody", {"class": "table-body"}).find_all("tr")
            result = []

            if "azalan" in url:
                sembol = "⛔️"
            elif "artan" in url:
                sembol = "💹"
            # burada aynı sonuçlar çıkınca twitter kopya paylaşım sanmasın diye başlıkları değiştiriyoruz.
            if ar==1:
                if sayac % 3 == 0:
                    result.append("Günün Dikkat Çeken Hisseleri (anlık)")
                elif sayac % 3 == 1:
                    result.append("Günün En Çok Artan Hisseleri (anlık)")
                elif sayac % 3 == 2:
                    result.append("Günün En Çok Artan ve Azalan Hisseleri")

            for veri in tbody[0:5]:
                if(str(veri.find_all("td")[0].find("a").text.strip()) == "ISBTR"):
                    veri = tbody[5]
                hisse = veri.find_all("td")
                hisse_adi = hisse[0].find("a").text.strip()
                hisse_alis = hisse[2].text.strip()
                if(hisse_alis == "-"):
                    hisse_alis = hisse[3].text.strip()
                    if(hisse_alis == "-"):
                        hisse_alis = hisse[1].text.strip()
                hisse_fark = hisse[4].text.strip()
                result.append("#" + str(hisse_adi) + " " + sembol + str(hisse_fark) + " " + str(hisse_alis) + "TL")

            metin = "\n".join(result)
            return metin

        azalan_url = "https://www.getmidas.com/canli-borsa/en-cok-azalan-hisseler"
        artan_url = "https://www.getmidas.com/canli-borsa/en-cok-artan-hisseler"

        # ar , artan url için scrap yapıldıgında 1 olmasını istiyorum çünkü bu sefer aynı başlığı iki defa yazmak zorunda kalacak.
        ar=1
        artan_metin = scrape(artan_url, sayac,ar)
        ar=0
        azalan_metin = scrape(azalan_url, sayac,ar)
    
        send_twitter = artan_metin + "\n\n" + azalan_metin

        #metin uzunluğu 280 dan fazla olması halinde twitter üyeliğimiz business değilse hata vermemesi için önlem alıyoruz.
        if(len(send_twitter) > 280):
            send_twitter = send_twitter[0:280]

        payload = {"text": str(send_twitter)}


        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            print(send_twitter)
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )

        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        sayac = sayac + 1
        # 1 saatte bir çalışırıyoruz.
        time.sleep(3600)

    except Exception as e:
        print(e)
        #olası bir hatada pas geçsin.
        continue

    