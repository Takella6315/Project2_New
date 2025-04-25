from django.shortcuts import render

def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'LandingPage/index.html', {'template_data': template_data})


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'LandingPage/about.html', {'template_data':template_data})