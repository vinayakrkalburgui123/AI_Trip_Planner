from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm
from trips.models import Trip


# ==========================
# Home Page
# ==========================

def home(request):
    return render(request, "home.html")


# ==========================
# Register
# ==========================

def register_user(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Registration successful! Please login."
            )

            return redirect("login")

        else:

            messages.error(
                request,
                "Registration failed. Please check the details below."
            )

    else:

        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


# ==========================
# Login
# ==========================

def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                f"Welcome {user.username}!"
            )

            return redirect("dashboard")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(request, "login.html")


# ==========================
# Logout
# ==========================

def logout_user(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("login")


# ==========================
# Dashboard
# ==========================

@login_required
def dashboard(request):

    trips = Trip.objects.filter(
        user=request.user
    )

    return render(
        request,
        "dashboard.html",
        {
            "trips": trips
        }
    )