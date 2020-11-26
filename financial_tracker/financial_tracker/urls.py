"""financial_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from main import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    url('signup/', main_views.signup, name='signup'),
    url('choose_purse/', main_views.choose_purse, name='choose_purse'),
    url('display_table/', main_views.display_table, name='display_table'),
    path('transactions/<int:purse_id>', main_views.transactions),
    path('upload_transactions/<int:purse_id>', main_views.upload_transactions),
    url('save_cat/', main_views.save_categories),
    url('categories/', main_views.categories, name='categories'),
    url('display_charts/', main_views.display_charts),
]
