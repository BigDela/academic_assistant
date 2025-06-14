#"""
#ASGI config for academic_assistant project.

###https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
#"""

#import os
#from resources.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
#from django.core.asgi import get_asgi_application
#import resources.routing  # adjust to match your app name

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_assistant.settings')

#application = ProtocolTypeRouter({
#    "http": get_asgi_application(),
 #   "websocket": AuthMiddlewareStack(
  #      URLRouter(
   #         resources.routing.websocket_urlpatterns
#        )
 #   ),
#})
