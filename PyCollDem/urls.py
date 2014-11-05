from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^account/$', 'CollDem.account_views.account'),
    url(r'^account/follow/(?P<userId>\d*)$', 'CollDem.account_views.follow'),
    url(r'^profile/$', 'CollDem.account_views.profile'),
    url(r'^register/$', 'CollDem.account_views.register'),
    url(r'^register/confirm/?(?P<userId>\d*)/$', 'CollDem.account_views.registerConfirm'),
    url(r'^profile/(?P<username>\w*)/$', 'CollDem.account_views.profile'),
    url(r'^profile/(?P<userId>\d*)/$', 'CollDem.account_views.profile'),
    url(r'^(?P<urlMsgId>\w*)$', 'CollDem.views.home'),

    #actions
    url(r'^logout/$', 'CollDem.views.logout_view'),
    url(r'^answer/$', 'CollDem.messageViews.answer'),
    url(r'^messages/delete/(?P<msgid>\w+)$', 'CollDem.messageViews.delete'),
   	url(r'^messages/evaluate/(?P<msgid>\w+)$', 'CollDem.messageViews.evaluate'),

    #message queries
    url(r'^messages/answer/(?P<answer_to>\w+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/author/(?P<authorid>\d+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/(?P<userid>\d+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/(?P<msgid>\w+)$', 'CollDem.messageViews.messages'),

    url(r'^media/eval/(?P<msgid>\w+)$', 'CollDem.messageViews.evaluation'),

	url(r'^facebook/', include('django_facebook.urls')),
	url(r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.
)

if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
)
