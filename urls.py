from django.conf.urls import url
from rest_framework import routers
from .views import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'contents', views.ContentsViewSet)

app_name = 'bonghwa'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    #auth
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.authentication, name='authentication'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^passChg/$', views.passChg, name='passChg'),

    #contents
    url(r'^insertContents/$', views.InsertContents.as_view(), name='insertContents'),
    url(r'^api/(?P<api>[a-z]+)/cpage/(?P<cpage>[0-9]+)', views.GetContents.as_view()),
    url(r'^api/deleteConts/(?P<id>[0-9]+)/', views.DeleteContents.as_view()),
    url(r'^api/viewMention/', views.ViewMention.as_view(), name='viewMention'),
    url(r'^new/(?P<created_date>[0-9]+)/', views.Newfirewood.as_view()),

    #webSocket
    url(r'^activeSession/$', views.ActiveSession.as_view(), name='activeSession'),
    url(r'^deactiveSession/$', views.DeActiveSession.as_view(), name='deactiveSession'),
    url(r'^getSession/$', views.GetSession.as_view(), name='getSession'),
]