import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import CarDealer, DealerReview
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                            params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
# def post_request(url, **kwargs):
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    response = None
    try:
        # Call post method of requests library with URL and parameters
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                 params=kwargs, json=payload)
        response.raise_for_status()  # Raise an exception if the response status code indicates an error
        json_data = response.json() if response.text else None  # Check if response text is not empty before parsing as JSON
    except requests.exceptions.RequestException as e:
        print("Network exception occurred:", str(e))
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", str(e))
    else:
        status_code = response.status_code
        print("With status {} ".format(status_code))
        return json_data



# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"]
            )
            results.append(dealer_obj)

    return results

def get_dealer_from_cf(url, dealer_id, **kwargs):
    json_result = get_request(url, id=dealer_id)
    dealer = None
    if json_result:
        dealer_doc = json_result[0]  # Assuming there is only one dealer in the result
        dealer = CarDealer(
            address=dealer_doc["address"],
            city=dealer_doc["city"],
            full_name=dealer_doc["full_name"],
            id=dealer_doc["id"],
            lat=dealer_doc["lat"],
            long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"],
            zip=dealer_doc["zip"]
        )
    return dealer


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    json_result = get_request(url, ID=dealer_id)
    if json_result:
        reviews = json_result['data']['docs']
        for review in reviews:
            try:
                review_obj = DealerReview(
                    name=review["name"], 
                    dealership=review["dealership"], 
                    review=review["review"], 
                    purchase=review["purchase"],
                    purchase_date=review["purchase_date"], 
                    car_make=review.get('car_make', 'none'),
                    car_model=review.get('car_model', 'none'), 
                    car_year=review.get('car_year', 'none'), 
                    sentiment= "none", 
                    id=review.get('id', 'none')
                )
                results.append(review_obj)
            except KeyError as e:
                print("KeyError occurred while processing review:", str(e))
            except Exception as e:
                print("Error occurred while processing review:", str(e))

     # Perform sentiment analysis for all reviews
    for review_obj in results:
        review_obj.sentiment = analyze_review_sentiments(review_obj.review)

    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    if len(text) < 20:
        return "none"

    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/c696d0fd-e354-445a-8b67-3d409d4fc13b"
    api_key = "Lwm6eaTG9PaH_vg5f6TCi1gTENTKpnmlOnByQIVFszb0"
    
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2020-08-01',
    authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=text,
        features= Features(sentiment= SentimentOptions())
    ).get_result()
    print(json.dumps(response))
    sentiment_score = str(response["sentiment"]["document"]["score"])
    sentiment_label = response["sentiment"]["document"]["label"]
    print(sentiment_score)
    print(sentiment_label)
    sentimentresult = sentiment_label
    
    return sentimentresult



def store_review(url, payload, **kwargs):
    post_request(url, payload=payload)




