from django.urls import path
from UserManagement import views

urlpatterns = [
    path('', views.get_login_page, name='get_login_page'),
    path('user', views.authenticate_user, name='authenticate_user'),
    path('dashboard', views.get_dashboard, name='dashboard'),
    path('filter_dashboard', views.filter_dashboard, name='filter_dashboard'),
    path('logout', views.logout, name='logout'),
    path('geo_maps', views.get_geo_maps_page, name='geo_maps'),
    path('team_management', views.get_team_management_page, name='team_management'),
    path('location_management', views.get_location_management_page, name='location_management'),
    path('methods', views.get_methods_page, name='methods'),
    path('health_education', views.get_health_education_report, name='health_education'),
    path('chw_performance', views.get_chw_performance_report, name='chw_performance'),
    path('clients_summary', views.get_client_summary, name='clients_summary'),
    path('filter_clients', views.get_filtered_client_summary, name='filter_clients'),
    path('referrals_summary', views.get_referrals_summary, name='referrals_summary'),
    path('visits_summary', views.get_visit_summary, name='visits_summary'),
    path('initiations_summary', views.get_initiations_summary, name='initiations_summary'),
    path('discontinuations_summary', views.get_discontinuations_summary, name='discontinuations_summary'),
    path('citizens_report_summary', views.get_citizen_report_summary, name='citizens_report_summary')

]