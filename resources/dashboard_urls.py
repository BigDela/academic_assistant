from django.urls import path
from . import dashboard_views

urlpatterns = [
    path('', dashboard_views.home, name='home'),
    # Notification endpoints
    path('notifications/', dashboard_views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/', dashboard_views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/mark-all-read/', dashboard_views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/unread-counts/', dashboard_views.get_unread_counts, name='get_unread_counts'),
]
