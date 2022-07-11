from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(
        title='Discussion Forum API',
        description='a simple api for question and answer.',
        default_version='v1',
        terms_of_service='https://www.google.com/policies/terms/',
    ),
    public=True,
    permission_classes=(AllowAny,),
)

v1_urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('discuss/', include('thread.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/register/', include('dj_rest_auth.registration.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    re_path(r'^api/v1/', include((v1_urlpatterns, 'v1'), namespace='v1')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
