from django.shortcuts import render, get_object_or_404, redirect

def home(request):
    return redirect("payment/")
    return render(request, "home.html")
