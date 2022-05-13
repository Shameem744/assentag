"""facebook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.registration),
    path('login/',views.login),
    path('logout/',views.logout_function),
    path('profile/',views.profile),
    path('comment/<int:id>/',views.comment),
    path('edit_profile/',views.edit_profile),
    path('password/',views.change_password),
    path('like/', views.like),
    path('delete-post/<int:id>/', views.delete_post),
    path('profile/user/<int:id>/', views.user_profile),
    path('follow/user/<int:id>/', views.follow_user),
    path('search/ajax/', views.search_user),
    path('following/list/<int:id>/',views.list_following),
    path('follower/list/<int:id>/',views.list_followers),
    path('allow/<int:id>/',views.allow_image),
    path('blur/<int:id>/',views.blur_image),
    path('notifications/', views.notifications),
    path('chat/',views.chat_home),
    path('chat/<int:id>/',views.chat_box)


]
