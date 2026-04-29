from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Post(models.Model):
    KATEGORIYA_CHOICES = [
        ('texnologiya', 'Texnologiya'),
        ('hayot', 'Hayot'),
        ('sport', 'Sport'),
    ]

    sarlavha = models.CharField(max_length=200, db_index=True)  # Index
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    rasm = models.ImageField(upload_to='postlar/', blank=True, null=True)
    yaratilgan_sana = models.DateTimeField(auto_now_add=True, db_index=True)
    yangilangan_sana = models.DateTimeField(auto_now=True)
    nashr_etilgan = models.BooleanField(default=True)
    korildi = models.IntegerField(default=0)

    class Meta:
        ordering = ['-yaratilgan_sana']
        indexes = [
            models.Index(fields=['-yaratilgan_sana', 'nashr_etilgan']),
        ]

    def __str__(self):
        return self.sarlavha


class Izoh(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='izohlar')
    muallif = models.ForeignKey(User, on_delete=models.CASCADE)
    matn = models.TextField()
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Izoh: {self.muallif.username} - {self.post.sarlavha}'


class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='layklar')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f'{self.user.username} liked {self.post.sarlavha}'


class Profil(models.Model):
    foydalanuvchi = models.OneToOneField(User, on_delete=models.CASCADE)
    rasm = models.ImageField(upload_to='profillar/', default='profillar/default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    tugilgan_sana = models.DateField(null=True, blank=True)
    manzil = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.foydalanuvchi.username} profili"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Rasmni kichraytirish. Fayl topilmasa profil saqlanishi to‘xtab qolmasin.
        try:
            img = Image.open(self.rasm.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.rasm.path)
        except (FileNotFoundError, ValueError):
            pass
