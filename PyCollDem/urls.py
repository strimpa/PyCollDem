from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'CollDem.views.home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/', 'CollDem.views.logout_view'),
    url(r'^messages/(\d*)', 'CollDem.messageViews.messages'),
)
