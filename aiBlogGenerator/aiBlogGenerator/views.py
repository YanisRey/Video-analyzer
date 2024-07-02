from django.shortcuts import render


def homepage(request):
    return render(request, 'index.html')
def login(request):
    return render(request, 'login.html')
def signup(request):
    return render(request, 'signup.html')
def allBlogs(request):
    return render(request, 'all-blogs.html')
def blogDetails(request):
    return render(request, 'blog-details.html')