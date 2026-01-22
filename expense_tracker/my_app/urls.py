from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
    path('budget/set/', views.set_budget, name='set_budget'),
    
    path('reports/', views.reports, name='reports'),
    path('export/csv/', views.export_expenses_csv, name='export_expenses_csv'),
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='my_app/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('ajax/add_category/', views.ajax_add_category, name='ajax_add_category'),
]