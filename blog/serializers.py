from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    muallif = serializers.PrimaryKeyRelatedField(read_only=True)
    muallif_ismi = serializers.CharField(source='muallif.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'sarlavha',
            'matn',
            'muallif',
            'muallif_ismi',
            'rasm',
            'yaratilgan_sana',
            'yangilangan_sana',
            'nashr_etilgan',
            'korildi',
        ]
        read_only_fields = ['id', 'muallif', 'muallif_ismi', 'yaratilgan_sana', 'yangilangan_sana', 'korildi']
