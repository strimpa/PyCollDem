from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^facebook/', include('django_facebook.urls')),
	url(r'^accounts/', include('django_facebook.auth_urls')), #Don't add this line if you use django registration or userena for registration and auth.

    #message queries
    url(r'^messages/answers/(?P<answer_to>\w+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/author/(?P<authorid>\d+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/(?P<userid>\d+)$', 'CollDem.messageViews.messages'),
    url(r'^messages/(?P<msgid>\w+)$', 'CollDem.messageViews.messages'),

    url(r'^notifications/json/', 'CollDem.analytics.notifications'),
    url(r'^media/eval/(?P<msgid>\w+)$', 'CollDem.messageViews.evaluation'),

    url(r'^search_twitter/$', 'CollDem.views.search_twitter'),
    
    # Main content urls:
    url(r'^admin/$', include(admin.site.urls)),
    url(r'^account/$', 'CollDem.views.account'),
    url(r'^account/follow/(?P<userId>\d*)$', 'CollDem.account_views.follow'),
    url(r'^profile/$', 'CollDem.views.profile'),
    url(r'^register/$', 'CollDem.views.register'),
    url(r'^register/confirm/?(?P<userId>\d*)/$', 'CollDem.account_views.registerConfirm'),
    url(r'^profile/(?P<userId>\d+)/$', 'CollDem.views.profile'),
    url(r'^profile/(?P<username>\w*)/$', 'CollDem.views.profile'),
    url(r'^(?P<urlMsgId>\w*)$', 'CollDem.views.home'),
    url(r'^notifications/', 'CollDem.views.notification_view'),

    #actions
    url(r'^login/$', 'CollDem.account_views.login_request'),
    url(r'^logout/$', 'CollDem.account_views.logout_request'),
    url(r'^answer/$', 'CollDem.messageViews.answer'),
    url(r'^messages/delete/(?P<msgid>\w+)$', 'CollDem.messageViews.delete'),
   	url(r'^messages/evaluate/(?P<msgid>\w+)$', 'CollDem.messageViews.evaluate'),

)

if settings.DEBUG:
	urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
)
