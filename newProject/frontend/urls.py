from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),          # http://127.0.0.1:8000/
    path('about/', views.about, name='about'),  # http://127.0.0.1:8000/about/
    path('contact/', views.contact, name='contact'),  # http://127.0.0.1:8000/contact/
    path('booking/', views.create_booking, name='create_booking'),
    path('properties/', views.allProperties, name='allProperties'),
    path('applying/', views.applying, name='applying'),
    # path('property_details/', views.property_details, name='property_details,'),
    path('property/<int:property_id>/', views.property_details, name='property_details'),

    path('home/', views.dasboardIndex, name="dasboardIndex"),
    path('listning/', views.dashboardListning, name="dashboardListning"),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/create/', views.blog_create, name='blog_create'),
    path('blogs/<int:pk>/edit/', views.blog_update, name='blog_update'),
    path('blogs/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('thankyou/', views.thankyou, name="thankyou"),
    path('schedule/', views.schedule, name='schedule'),
    path('update-booking-status/', views.update_booking_status, name='update_booking_status'),
    path('listning/add/', views.add_property, name='add_property'),
    path('listning/<int:pk>/delete/', views.delete_property, name='delete_property'),
    path('listning/<int:pk>/edit/', views.update_property, name='update_property'),
    path('property/<int:pk>/expire/', views.expire_property, name='expire_property'),
    path('property/<int:pk>/stats/', views.property_stats, name='property_stats'),
    path('add-application/', views.add_application, name='add_application'),
    path('applyingListing/', views.applyingList, name="applyingListDashboard"),
    path("application/<int:id>/", views.application_detail, name="application_view"),
    path('application/<int:id>/delete/', views.application_delete, name='application_delete'),
    path('applying/<int:pk>/edit/', views.edit_applying, name='edit_applying'),
    path('blog_show/', views.blog_show, name="blogShow"),
    path('blog_detail/<int:id>/', views.blogs_details, name="blogDetails"),
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('email_sender/', views.emailTemplate, name="email_template"),
    path('email_show/', views.email_show, name="email_show"),
]
