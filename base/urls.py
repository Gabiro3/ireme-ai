from django.urls import path
from . import views
urlpatterns = [
    path('register', views.registerPage, name="register"),
    path('login', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name="upload-file"),
    path('delete-file/<str:pk>', views.delete_file, name="delete-file"),
    path('view-files/grid', views.view_files_grid, name="view-files"),
    path('view-files/list', views.view_files_list, name="view-files-list"),
    path('file-details/<str:pk>/', views.file_details , name="file-details"),
    path('profile/', views.user_profile, name="profile"),
    path('search/', views.search_page, name="search"),
    path('coming-soon/', views.under_construction, name="coming-soon"),
    path('pricing/', views.pricing, name="pricing"),
]