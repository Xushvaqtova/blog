from django.urls import path, include
from django.conf.urls.static import static
from saytim import settings
from . import views
from rest_framework.routers import DefaultRouter

# Router yaratish
router = DefaultRouter()
router.register(r'postlar', views.PostViewSet, basename='post')


urlpatterns = [
    path('', views.bosh_sahifa, name='bosh_sahifa'),
    path('biz-haqimizda/', views.biz_haqimizda, name='biz_haqimizda'),
    path('aloqa/', views.aloqa, name='aloqa'),
    path('portfolio/', views.portfolio, name='portfolio'),
    
    # DIQQAT: Aniq manzillar (static) har doim dinamik manzillardan (<str>, <int>) YUQORIDA bo'lishi kerak!
    path('profil/tahrirlash/', views.profil_tahrirlash, name='profil_tahrirlash'),
    
    # Bu qator endi pastda turibdi, shuning uchun 'tahrirlash' so'zi bu yerga kelmaydi
    path('profil/<str:username>/', views.profil, name='profil'),
    
    path('post/<int:post_id>/', views.post_batafsil, name='post_batafsil'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'), 
    
    path('ommabop/', views.ommabop_postlar, name='ommabop'),
    
    path('post/<int:post_id>/tahrirlash/', views.post_tahrirlash, name='post_tahrirlash'),
    path('post/<int:post_id>/ochirish/', views.post_ochirish, name='post_ochirish'),
    
    path('royxatdan-otish/', views.royxatdan_otish, name='royxatdan_otish'),
    path('kirish/', views.kirish, name='kirish'),
    path('chiqish/', views.chiqish, name='chiqish'),
    
    path('yangi/', views.post_yaratish, name='post_yaratish'),
    
    path('qidiruv/', views.qidiruv, name='qidiruv'),

    path('api/postlar/', views.post_list_api, name='post_list_api'),
    path('api/postlar/<int:post_id>/', views.post_detail_api, name='post_detail_api'),
    path('api/postlar/<int:post_id>/yangilash/', views.post_update_api, name='post_update_api'),
    path('api/postlar/<int:post_id>/ochirish/', views.post_delete_api, name='post_delete_api'),

    path('api/', include(router.urls)),

    path('api/kirish/', views.login_api, name='login_api'),
    path('api/chiqish/', views.logout_api, name='logout_api'),
    path('api/royxatdan-otish/', views.register_api, name='register_api'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)