from django.shortcuts import render

# Landing page view
def landing_page(request):
    return render(request, 'index.html')

from django.shortcuts import render

def admin_console(request):
    return render(request, 'admin.html')


# views.py
from django.shortcuts import render
def timetable_builder(request):
    return render(request, 'timetable_builder.html')

# urls.py
