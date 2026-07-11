from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from trips.models import Trip


def home(request):
    return render(request, 'home.html')


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):

    trips = Trip.objects.filter(user=request.user)

    return render(
        request,
        'dashboard.html',
        {
            'trips': trips
        }
    )