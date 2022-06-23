from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import debug_toolbar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/discuss/', include('thread.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
