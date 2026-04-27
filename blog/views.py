from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Post, Izoh, Like, Profil
from .forms import PostForma, RoyxatdanOtishForma, IzohForma, FoydalanuvchiYangilashForma, ProfilYangilashForma
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PostSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User








# -------------------------------------------------------------------------------------




@api_view(['POST'])
def register_api(request):
    """Ro'yxatdan o'tish"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response(
            {'xato': 'Bu username band'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    token = Token.objects.create(user=user)

    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_api(request):
    """API orqali kirish"""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response(
            {'xato': 'Noto\'g\'ri login yoki parol'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def logout_api(request):
    """API orqali chiqish"""
    if request.user.is_authenticated:
        request.user.auth_token.delete()
        return Response({'xabar': 'Muvaffaqiyatli chiqildi'})
    return Response(
        {'xato': 'Tizimga kirilmagan'},
        status=status.HTTP_400_BAD_REQUEST
    )



class PostViewSet(viewsets.ModelViewSet):
    """
    Post lar uchun ViewSet
    - list: Barcha postlar
    - create: Yangi post
    - retrieve: Bitta post
    - update: Postni yangilash
    - destroy: Postni o'chirish
    """
    queryset = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Yangi post yaratishda muallif ni avtomatik qo'shish"""
        serializer.save(muallif=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Bitta post olishda korildi sonini oshirish"""
        instance = self.get_object()
        instance.korildi += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ommabop(self, request):
        """Eng ko'p ko'rilgan postlar"""
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mening_postlarim(self, request):
        """Foydalanuvchining o'z postlari"""
        if not request.user.is_authenticated:
            return Response(
                {'xato': 'Tizimga kirish kerak'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        postlar = Post.objects.filter(muallif=request.user).order_by('-yaratilgan_sana')
        serializer = self.get_serializer(postlar, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def post_list_api(request):
    """Barcha postlarni olish"""
    postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
    serializer = PostSerializer(postlar, many=True)
    return Response(serializer.data)





# ----------------------------------------------------------------------------------------------







def bosh_sahifa(request):
    postlar_list = Post.objects.select_related('muallif').filter(
        nashr_etilgan=True
    ).order_by('-yaratilgan_sana')

    # Har sahifada 5 ta post
    paginator = Paginator(postlar_list, 5)

    sahifa_raqami = request.GET.get('sahifa')
    postlar = paginator.get_page(sahifa_raqami)

    return render(request, 'blog/bosh.html', {'postlar': postlar})

def biz_haqimizda(request):
    return render(request, 'blog/biz_haqimizda.html')

def aloqa(request):
    return render(request, 'blog/aloqa.html')

def portfolio(request):
    return render(request, 'blog/portfolio.html')

def ommabop_postlar(request):
    postlar = Post.objects.filter(nashr_etilgan=True).order_by('-korildi')[:5]
    context = {'postlar': postlar}
    return render(request, 'blog/ommabop.html', context)

def post_batafsil(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Ko'rishlar sonini oshirish
    post.korildi += 1
    post.save(update_fields=['korildi'])

    # Like holatini tekshirish
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(post=post, user=request.user).exists()

    # Izoh qo'shish logikasi
    if request.method == 'POST':
        if request.user.is_authenticated:
            forma = IzohForma(request.POST)
            if forma.is_valid():
                izoh = forma.save(commit=False)
                izoh.post = post
                izoh.muallif = request.user
                izoh.save()
                messages.success(request, "✅ Izoh qoldirildi!")
                return redirect('post_batafsil', post_id=post.id)
        else:
            messages.error(request, "❌ Izoh qoldirish uchun tizimga kiring.")

    izohlar = post.izohlar.all().order_by('-yaratilgan_sana')

    context = {
        'post': post,
        'izohlar': izohlar,
        'user_liked': user_liked,
    }
    return render(request, 'blog/post_batafsil.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_obj, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        like_obj.delete()
        messages.info(request, "Like olib tashlandi")
    else:
        messages.success(request, "👍 Post yoqti!")
        
    return redirect('post_batafsil', post_id=post.id)

# Bitta aniq 'profil' funksiyasi
def profil(request, username):
    foydalanuvchi = get_object_or_404(User, username=username)
    postlar = Post.objects.filter(muallif=foydalanuvchi, nashr_etilgan=True).order_by('-yaratilgan_sana')

    context = {
        'profil_egasi': foydalanuvchi,
        'postlar': postlar,
        'postlar_soni': postlar.count()
    }
    return render(request, 'blog/profil.html', context)

def qidiruv(request):
    soz = request.GET.get('q', '')
    postlar = Post.objects.filter(
        Q(sarlavha__icontains=soz) | Q(matn__icontains=soz),
        nashr_etilgan=True
    )

    return render(request, 'blog/qidiruv.html', {
        'postlar': postlar,
        'soz': soz
    })

@login_required
def post_yaratish(request):
    if request.method == 'POST':
        forma = PostForma(request.POST, request.FILES)
        if forma.is_valid():
            post = forma.save(commit=False)
            post.muallif = request.user
            post.save()
            messages.success(request, '✅ Post yaratildi!')
            return redirect('bosh_sahifa')
    else:
        forma = PostForma()
    return render(request, 'blog/post_yaratish.html', {'forma': forma})

@login_required
def post_tahrirlash(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.muallif != request.user:
        messages.error(request, '❌ Siz faqat o\'z postingizni tahrirlashingiz mumkin!')
        return redirect('post_batafsil', post_id=post.id)

    if request.method == 'POST':
        forma = PostForma(request.POST, instance=post)
        if forma.is_valid():
            forma.save()
            messages.success(request, '✅ Post yangilandi!')
            return redirect('post_batafsil', post_id=post.id)
    else:
        forma = PostForma(instance=post)

    context = {'forma': forma, 'post': post}
    return render(request, 'blog/post_tahrirlash.html', context)

@login_required
def post_ochirish(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, '✅ Post o\'chirildi!')
        return redirect('bosh_sahifa')
    return render(request, 'blog/post_ochirish.html', {'post': post})

def royxatdan_otish(request):
    if request.method == 'POST':
        forma = RoyxatdanOtishForma(request.POST)
        if forma.is_valid():
            user = forma.save()
            login(request, user)
            messages.success(request, f'✅ Xush kelibsiz, {user.username}!')
            return redirect('bosh_sahifa')
    else:
        forma = RoyxatdanOtishForma()
    return render(request, 'blog/royxatdan_otish.html', {'forma': forma})

def kirish(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Xush kelibsiz, {user.username}!')
            return redirect('bosh_sahifa')
        else:
            messages.error(request, '❌ Noto\'g\'ri foydalanuvchi nomi yoki parol!')
    return render(request, 'blog/kirish.html')

def chiqish(request):
    logout(request)
    messages.info(request, '👋 Xayr! Tez orada qaytib kelasiz!')
    return redirect('bosh_sahifa')

@login_required
def profil_tahrirlash(request):
    # 1. PROFIL MAVJUDLIGINI TEKSHIRISH VA YARATISH (Xavfsizlik)
    try:
        profil_obj = request.user.profil
    except Profil.DoesNotExist:
        # Agar profil yo'q bo'lsa, yangisini yaratamiz
        profil_obj = Profil.objects.create(foydalanuvchi=request.user)

    if request.method == 'POST':
        f_forma = FoydalanuvchiYangilashForma(request.POST, instance=request.user)
        p_forma = ProfilYangilashForma(request.POST, request.FILES, instance=profil_obj)

        if f_forma.is_valid() and p_forma.is_valid():
            f_forma.save()
            p_forma.save()
            messages.success(request, '✅ Profilingiz yangilandi!')
            return redirect('profil', username=request.user.username)
    else:
        f_forma = FoydalanuvchiYangilashForma(instance=request.user)
        p_forma = ProfilYangilashForma(instance=profil_obj)

    context = {
        'f_forma': f_forma,
        'p_forma': p_forma
    }
    return render(request, 'blog/profil_tahrirlash.html', context)


@api_view(['GET', 'POST'])
def post_list_api(request):
    if request.method == 'GET':
        # Olish
        postlar = Post.objects.filter(nashr_etilgan=True).order_by('-yaratilgan_sana')
        serializer = PostSerializer(postlar, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Yaratish
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(muallif=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def post_detail_api(request, post_id):
    """Bitta postni olish"""
    try:
        post = Post.objects.get(id=post_id, nashr_etilgan=True)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

    # korildi sonini oshirish
    post.korildi += 1
    post.save()

    serializer = PostSerializer(post)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
def post_update_api(request, post_id):
    """Postni yangilash"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Faqat muallif yangilay oladi
    if post.muallif != request.user:
        return Response(
            {'xato': 'Ruxsat yo\'q'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = PostSerializer(post, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def post_delete_api(request, post_id):
    """Postni o'chirish"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response(
            {'xato': 'Post topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Faqat muallif o'chira oladi
    if post.muallif != request.user:
        return Response(
            {'xato': 'Ruxsat yo\'q'},
            status=status.HTTP_403_FORBIDDEN
        )

    post.delete()
    return Response(
        {'xabar': 'Post o\'chirildi'},
        status=status.HTTP_204_NO_CONTENT
    )