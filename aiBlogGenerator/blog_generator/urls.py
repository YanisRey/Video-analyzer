from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('blog-details/<int:pk>/', views.blog_details, name="blog-details"),
    path('generate-blog/', views.generate_blog, name="generate-blog"),
    path('blog-list/', views.blog_list, name="blog-list"),
    path('generate-ts/', views.generate_ts, name="generate-ts"),
]
