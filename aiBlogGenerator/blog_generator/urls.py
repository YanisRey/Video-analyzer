from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login/', views.user_login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('all-blogs/', views.allBlogs, name="all-blogs"),
    path('blog-details/', views.blogDetails, name="blog-details"),
    path('generate-blog/', views.generate_blog, name="generate-blog"),
]
