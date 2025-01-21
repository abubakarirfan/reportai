from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_report, name='upload_report'),
    path('signup/', views.signup, name='signup'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('list/', views.report_list, name='report_list'),
    path('<int:pk>/rename/', views.rename_report_file, name='rename_report_file'),

]
