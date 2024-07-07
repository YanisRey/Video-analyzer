from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('signup/', views.signup, name="signup"),
    path('blog-list/blog-details/<int:pk>/', views.blog_details, name="blog-details-from-list"),
    path('blog-details/<int:pk>/', views.blog_details, name="blog-details"),
    path('generate-blog/', views.generate_blog, name="generate-blog"),
    path('blog-list/', views.blog_list, name="blog-list"),
    path('generate-ts/', views.generate_ts, name="generate-ts"),
    path('save-blog/', views.save_blog, name="save-blog"),
    path('delete/<int:pk>/', views.delete_blog, name="delete-blog"),
    path('delete-all/', views.delete_all, name="delete-all"),
]
