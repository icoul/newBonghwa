import datetime
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
import json
from ..models import Contents
from ..serializers import UserSerializer, ContentsSerializer
from ..forms import UserForm, ContentsForm, LoginForm

from rest_framework import viewsets, mixins, status, generics
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

import re

list = []   #접속자 리스트?

# class LoginSession(TemplateView):
#     template_name = 'index.html'
#
#     def post(self, request, *args, **kwargs):
#         redis_publisher = RedisPublisher(facility='foobar', users=[request.POST.get('user')])
#         message = RedisMessage(request.POST.get('message'))
#         redis_publisher.publish_message(message)
#         return HttpResponse('OK')


class ActiveSession(TemplateView):
    template_name = 'html/user.html'

    def post(self, request, *args, **kwargs):
        username = request.session['username']

        if username in list or username == '':
            return HttpResponse('OK')

        list.append(username)
        return HttpResponse('OK')


class DeActiveSession(TemplateView):
    template_name = 'html/user.html'

    def post(self, request, *args, **kwargs):
        username = request.session['username']
        list.remove(username)
        return HttpResponse('OK')


class GetSession(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse(json.dumps({'list': list}), content_type="application/json")


# api
class GetContents(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        api   = self.kwargs['api']
        cpage = self.kwargs['cpage']
        username = request.session['username']

        minimum = (int(cpage) - 1) * 20
        maximum = int(cpage) * 20

        if(api == 'all'):        # 전체글 가져오기
            contentsQuery = Contents.objects.all().order_by('-created_date').values()[minimum:maximum]
        elif(api == 'to'):       # 내가 쓴 글만 가져오기
            contentsQuery = Contents.objects.filter(username = username).order_by('-created_date').values()[minimum:maximum]
        elif(api == 'from'):     # 나에게 보낸 멘션만 가져오기
            contentsQuery = Contents.objects.filter(Q(contents__contains = ('@' + username)) | \
                            Q(contents__contains = ('!' + username))).order_by('-created_date').values()[minimum:maximum]
        
        contentList = createMention(contentsQuery, username)
        
        return JsonResponse({'contentList': contentList})


class Newfirewood(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        username = request.session['username']
        created_date = self.kwargs['created_date']
        contentsQuery = Contents.objects.filter(created_date__gt=created_date).values()
        contentList = createMention(contentsQuery, username)

        return JsonResponse({'contentList': contentList})


def createMention(contents, username):
    contentList = []
    pattern = re.compile('\![\u3131-\u3163\uac00-\ud7a3\w]+')
    nameP = re.compile('\!' + username)

    for query in contents:
        m = pattern.match(query['contents'])
        n = nameP.match(query['contents'])

        if m and not n:
            continue

        mention_id = query['id']
        mention_index = query['mention_index']
        mention_order = query['mention_order']
    
        results = Contents.objects.filter(Q(mention_index=mention_index) | Q(id=mention_index)) \
                                .filter(mention_order__lt=mention_order)\
                                .exclude(id=mention_id)\
                                .order_by('-created_date')\
                                .values()
        mention = '<ul>'
        
        for result in results:
            mention += ('<li>' + result['username'] + ' : ' + result['contents'] + '</li>')
        
        mention += '</ul>'
        query['mention'] = mention
        contentList.append(query)

    return contentList


class DeleteContents(GenericAPIView, mixins.ListModelMixin):
    def delete(self, request, id):
        content = Contents.objects.get(id=id)

        if request.method == 'DELETE':
            content.delete()
            return Response(status=status.HTTP_200_OK)


class ViewMention(GenericAPIView, mixins.ListModelMixin):
    def get(self, request):
        mention_id = self.request.query_params['id']
        mention_index = self.request.query_params['mention_index']
        mention_order = self.request.query_params['mention_order']

        if mention_index == '0':
            results = Contents.objects.filter(mention_index=mention_id).values()
        elif mention_index != '0':
            results = Contents.objects.filter(mention_index=mention_index) \
                                      .filter(mention_order__gt=mention_order)\
                                      .exclude(id=mention_id)\
                                      .values()

        content = []
        for result in results:
            content.append(result)

        return JsonResponse({'content': content})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ContentsViewSet(viewsets.ModelViewSet):
    queryset = Contents.objects.all()
    serializer_class = ContentsSerializer


def index(request):
    if not loginCheck(request):
        form = LoginForm
        return render(request, 'html/login.html', {'form': form})

    username = request.session['username']

    form = ContentsForm()
    return render(request, 'html/main.html', {'username': username, 'form': form})


class InsertContents(TemplateView):
    Model = Contents
    template_name = 'html/index.html'

    def post(self, request):
        username = request.session['username']

        if request.method == 'POST':
            form = ContentsForm(request.POST, request.FILES)

            if form.is_valid():
                today = datetime.datetime.now()
                firewood = form.save(commit=False)
                firewood.created_date = today.strftime('%Y%m%d%H%M%S%f')
                firewood.username = username
                firewood.save()
            return redirect('/')

        return redirect('/')


def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            return redirect('/')

    else:
        form = UserForm()
        return render(request, 'html/signup.html', {'form':form})


def authentication(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            request.session['username'] = username
            return redirect('/')
        else:
            return render(request, 'html/login.html', {'form': form, 'error':'로그인 망함'})

    else:
        form = LoginForm
        return render(request, 'html/login.html', {'form': form})


def passChg(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        username_check = User.objects.filter(username=username).count()

        if not username_check:
            return render(request, 'html/passChg.html', {'notFoundId':'0'})

        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()

        form = LoginForm
        return render(request, 'html/login.html', {'form': form})

    return render(request, 'html/passChg.html')



def logout(request):
    del request.session['username']

    return redirect('/')


def loginCheck(request):
    login_check = 'username' in request.session

    if login_check:
        return True
