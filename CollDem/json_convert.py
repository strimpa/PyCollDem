import json
from json import JSONEncoder
from CollDem.models import Message
from django.conf import settings
from django.conf.urls.static import static

class CollDemEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Message):
			return {
				'id':obj.guid,
				'author':obj.author.username,
				'avatar':'/media/'+settings.MEDIA_URL+obj.author.pic.url,
				'header':obj.header, 
				'text':obj.text,
				'can_delete':obj.canDelete
			}

		return JSONEncoder.default(self, obj)