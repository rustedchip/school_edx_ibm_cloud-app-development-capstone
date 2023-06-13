from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from . import restapis
from . import models



# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# Create an `about` view to render a static about page
# def about(request):
def about(request):
    return render(request, 'djangoapp/about.html')
# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
            # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username,first_name=first_name,last_name=last_name, password=password)
            user.save()
            user = authenticate(username=username, password=password)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships

#def get_dealerships(request):
#    context = {}
#    if request.method == "GET":
#        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...



# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = 'https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/get-dealership'
        # Get dealers from the URL
        context = {"dealerships": restapis.get_dealers_from_cf(url)}
        # Concat all dealer's short name
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/get-review'
        dealer_url = 'https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/get-dealership'
        context = {
            "reviews":  restapis.get_dealer_reviews_from_cf(url, dealer_id),
            "dealer":  restapis.get_dealer_from_cf(dealer_url, dealer_id)
        }
        
        return render(request, 'djangoapp/dealer_details.html', context)
    

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/get-dealership?ID={0}".format(dealer_id)
        dealer_url = 'https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/get-dealership'
        # Get dealers from the URL
        context = {
            "cars": models.CarModel.objects.all(),
            "dealer": restapis.get_dealer_from_cf(dealer_url, dealer_id)
        }
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == "POST":
        if request.user.is_authenticated:
            form = request.POST
            review = {
                "name": request.user.username,
                "dealership": dealer_id,
                "review": form["review"],
                "purchase": form.get("purchase_check"),
            }
            if form.get("purchase_check"):
                review["purchase_date"] = datetime.strptime(form.get("purchase_date"), "%Y-%m-%d").isoformat()
                car = models.CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.make.name
                review["car_model"] = car.name
                review["car_year"] = car.year.strftime("%Y")
            
            json_payload = {"review": review}
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/966665de-2727-4a83-b26d-23a33046c462/dealership-package/post-review"
            response = restapis.post_request(url, payload=json_payload)

            if response and response.get("success"):
                messages.success(request, "Review successfully submitted.")
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            else:
                messages.error(request, "Failed to submit review. Please try again.")
        else:
            return redirect("/djangoapp/login")

    # Return a default response
    return redirect("djangoapp:dealer_details", dealer_id=dealer_id)