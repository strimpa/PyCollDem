from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'PyCollDem.views.home', name='home'),
    url(r'^messages/(P<id>\d*)', 'PyCollDem.messageViews.messages'),

    url(r'^admin/', include(admin.site.urls)),
)
