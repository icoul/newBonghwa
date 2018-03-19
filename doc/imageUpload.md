Django 이미지 업로드  
===================  
  
models  
-------------------  
  
```python
class Contents(models.Model):
    mention_index = models.CharField(max_length=5, default='0')  # 멘션 index
    mention_order = models.CharField(max_length=5, default='0')  # 멘션 순서
    username = models.CharField(max_length=30)                   # 유저 아이디
    contents = models.CharField(max_length=150)                  # 장작 내용
    file = models.FileField(null=True)                           # 파일
    created_date = models.CharField(max_length=14)               # 작성일
    deleted = models.IntegerField(default=0)                     # 삭제여부

    def __str__(self):
        return self.contents
```
  
이미지를 업로드하기 위해 models단에 file명이 들어갈 file컬럼을 생성하였다.  
Field는 File이며 파일을 업로드하지 않을 수 있기 때문에 null=True를 주었다.  
  
settings  
------------------
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```
파일이 업로드 될 경로를 설정한다.  
MEDIA_URL은 향후 업로드, 다운로드, 뷰 등에 사용할 URL이며  
MEDIA_ROOT는 실제 파일이 저장되는 경로이다.  
이 프로젝트의 최상단인 Bonghwa폴더 바로 아래에 media폴더가 생성된다.  
  
urls  
------------------
```python
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('bonghwa.urls')),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
url은 앱에 위치한 urls가 아닌 프로젝트의 urls에 추가한다.  
django.conf.urls의 static 함수는 디버그 모드에서 미디어 파일 URL패턴을 제공하는 역할을 한다.  
settings에 설정했던 URL과 경로를 import해와서 넣어준다.  
  
forms  
------------------
```python
class ContentsForm(ModelForm):
    contents = forms.CharField(widget=forms.Textarea(attrs={'v-model': 'firewood_id', '@keydown.enter': 'insert_content'}))
    mention_index = forms.CharField(widget=forms.HiddenInput, initial='0')
    mention_order = forms.CharField(widget=forms.HiddenInput, initial='0')

    class Meta:
        model = Contents
        fields = ['contents', 'mention_index', 'mention_order', 'file']
```
ContentsForm의 fields에 file을 추가한다.  
  
>
> 현재로써 3가지 해결해야 할 요소가 존재하는데 
> 1. file fields의 구성요소에 대한 수정이 필요하다. django에서 Form을 쓰면 구성요소를 어떻게 바꿔야할지 고민이다.
> 2. \__init__ 함수를 통해 초기화를 하고 유효성 검사에 대한 설정을 해주고 싶은데 왠지 모르지만 에러가 난다.
> 3. file 업로드에 대한 form은 따로 만드는게 좋다고 하는데 이유도 모르겠고 어떻게 2개의 form을 동시에 돌리는지 모르겠다.
>
html  
------------------
```html
 <form id="insert_form" action="{% url 'bonghwa:insertContents' %}" method="post" enctype="multipart/form-data" novalidate>
    {% csrf_token %}
    {{ form.as_p }}
    <button id="submit_btn" type="submit">등록</button>
</form>
```  
form.as_p로 p태그 형태로 form이 생성되게 하고 enctype="multipart/form-data"를 추가한다.  
이는 POST 형태로 데이터를 전송할 때의 인코딩 방식을 설정하는 것으로 이렇게 설정해야 file타입의 input을 처리할 수 있다.  
novalidate는 파일을 올리지 않을 경우 null이 들어갈 수 있기 때문에 유효성 검사를 막는 것이다.  
  
views  
-----------------
```python
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
                firewood.created_date = today.strftime('%Y%m%d%H%M%S')
                firewood.username = username
                firewood.save()
            return redirect('/')

        return redirect('/')
```
이전과의 차이점은 ContentForm에 인자로 request.FILES가 추가되었다는 점이다.  
그 외에는 차이없으며 save()를 통해 form 데이터를 저장하면 자동으로 파일명이 file 컬럼에 저장된다.  
JAVA와 달리 original 파일명과 인코딩 된 파일명을 따로 저장할 필요 없이 original 파일명만 사용한다.  
  
>
> 현재로써는 위 forms 부분의 문제에 더해서 파일용량 제한이나 기타 업로드 형식 등과 같은 설정을
> 어디서 어떻게 하는지 알아보는 것이 중요하다.
>

이미지 view  
-----------------
view단에서 업로드 된 이미지를 확인하는 기능은 우선  
1. 이미지를 오픈하는 버튼  
2. 이미지를 보여줄 각 멘션에 붙어있는 div  
로 구성된다.  
이 중 div는 처음 로딩 될 때는 아무런 내용물도 없는 빈 껍데기이지만  
이미지를 오픈하는 '[이미지]' 버튼을 클릭하면 `<img src="{{ url }}">` 혹은 background에 해당 이미지의 url을 받아  
이미지를 보여주고 클릭하면 hide 된다.