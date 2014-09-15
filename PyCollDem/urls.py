from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^account/$', 'CollDem.account_views.account'),
    url(r'^profile/$', 'CollDem.account_views.profile'),
    url(r'^register/$', 'CollDem.account_views.register'),
    url(r'^profile/(?P<username>\w*)/$', 'CollDem.account_views.profile'),
    url(r'^profile/(?P<userId>\d*)/$', 'CollDem.account_views.profile'),
   	url(r'^register/$', 'CollDem.account_views.account'),
    url(r'^(?P<urlMsgId>\w*)$', 'CollDem.views.home'),

    #actions
    url(r'^logout/$', 'CollDem.views.logout_view'),
    url(r'^answer/$', 'CollDem.messageViews.answer'),
    url(r'^messages/delete/(?P<msgid>\w+)', 'CollDem.messageViews.delete'),

    #message queries
    url(r'^messages/answer/(?P<answer_to>\w+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/author/(?P<userid>\d+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/(?P<msgid>\w+)/$', 'CollDem.messageViews.messages'),

)

if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
)
