from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse

from .models import Trip

import google.generativeai as genai
import requests

from reportlab.pdfgen import canvas


# ----------------------------
# Configure Gemini
# ----------------------------

genai.configure(api_key=settings.GEMINI_API_KEY)

try:
    for m in genai.list_models():
        print("MODEL:", m.name)
except Exception as e:
    print("MODEL LIST ERROR:", e)


# ----------------------------
# Create Trip
# ----------------------------

def create_trip(request):

    plan = None
    weather = None
    image_urls = []

    if request.method == "POST":

        destination = request.POST.get("destination")
        days = request.POST.get("days")
        budget = request.POST.get("budget")
        preferences = request.POST.get("preferences")

        # ---------------------------------
        # PEXELS IMAGES
        # ---------------------------------

        try:

            headers = {
                "Authorization": settings.PEXELS_API_KEY
            }

            image_response = requests.get(
                f"https://api.pexels.com/v1/search?query={destination}&per_page=8",
                headers=headers
            )

            image_data = image_response.json()

            if image_data.get("photos"):

                for photo in image_data["photos"]:

                    image_urls.append(
                        photo["src"]["large"]
                    )

        except Exception as e:

            print("PEXELS ERROR:", e)

        # ---------------------------------
        # WEATHER API
        # ---------------------------------

        try:

            weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={destination}"
                f"&appid={settings.WEATHER_API_KEY}"
                f"&units=metric"
            )

            weather_response = requests.get(weather_url)

            weather_data = weather_response.json()

            if weather_response.status_code == 200:

                weather = {
                    "temp": weather_data["main"]["temp"],
                    "humidity": weather_data["main"]["humidity"],
                    "condition": weather_data["weather"][0]["description"].title()
                }

        except Exception as e:

            print("WEATHER ERROR:", e)

            weather = None

        # ---------------------------------
        # GEMINI
        # ---------------------------------

        prompt = f"""
You are a professional travel planner.

Create a detailed travel plan.

Destination: {destination}

Trip Duration: {days} days

Total Budget: ₹{budget}

Travel Preferences:
{preferences}

Current Weather:
{weather}

Create the response in the following format.

==================================================

🌍 Destination Overview

Give a short introduction.

==================================================

📅 Day-wise Itinerary

For each day include:

Morning

Afternoon

Evening

Night

Expected Expense for the Day

==================================================

💰 Budget Breakdown

Divide the total budget into:

Accommodation

Food

Transportation

Activities

Shopping

Emergency

Make sure the total equals exactly ₹{budget}.

==================================================

📊 Daily Expense Plan

Create a table like this.

Day 1

Hotel : ₹...

Food : ₹...

Transport : ₹...

Activities : ₹...

Shopping : ₹...

Total : ₹...

Repeat for every day.

==================================================

🎒 Packing Checklist

Suggest what to pack according to the destination and weather.

==================================================

💡 Money Saving Tips

Give 5 useful travel budget tips.

==================================================

🍽 Food Recommendations

Suggest famous local foods.

==================================================

⭐ Must Visit Places

Suggest famous tourist attractions.

"""
        try:

            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            response = model.generate_content(prompt)

            plan = response.text

            # ----------------------------
            # Budget Calculation
            # ----------------------------

            total_budget = int(budget)

            hotel_budget = int(total_budget * 0.40)
            food_budget = int(total_budget * 0.20)
            transport_budget = int(total_budget * 0.15)
            activities_budget = int(total_budget * 0.15)
            shopping_budget = int(total_budget * 0.05)

            emergency_budget = (
                total_budget
                - hotel_budget
                - food_budget
                - transport_budget
                - activities_budget
                - shopping_budget
            )

            Trip.objects.create(
                user=request.user,
                destination=destination,
                days=days,
                budget=budget,
                preferences=preferences,
                plan=plan,

                hotel_budget=hotel_budget,
                food_budget=food_budget,
                transport_budget=transport_budget,
                activities_budget=activities_budget,
                shopping_budget=shopping_budget,
                emergency_budget=emergency_budget,
            )

        except Exception as e:

            plan = f"Gemini Error: {e}"

    return render(
        request,
        "create_trip.html",
        {
            "plan": plan,
            "weather": weather,
            "image_urls": image_urls,
        }
    )


# ----------------------------
# DELETE TRIP
# ----------------------------

def delete_trip(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    trip.delete()

    return redirect("dashboard")


# ----------------------------
# VIEW TRIP
# ----------------------------

def view_trip(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    maps_url = (
        f"https://www.google.com/maps/search/?api=1&query={trip.destination}"
    )

    return render(
        request,
        "view_trip.html",
        {
            "trip": trip,
            "maps_url": maps_url,
        }
    )

# ----------------------------
# DOWNLOAD PDF
# ----------------------------

def download_pdf(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{trip.destination}_Trip.pdf"'

    pdf = canvas.Canvas(response)

    pdf.setTitle(
        f"{trip.destination} Trip Plan"
    )

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        50,
        800,
        f"{trip.destination} Trip Plan"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    y = 770

    for line in trip.plan.split("\n"):

        pdf.drawString(
            50,
            y,
            line[:100]
        )

        y -= 20

        if y < 50:

            pdf.showPage()

            pdf.setFont(
                "Helvetica",
                12
            )

            y = 800

    pdf.save()

    return response