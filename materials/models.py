from django.db import models

from config import settings


class Course(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Название", help_text="Введите название курса"
    )
    image = models.ImageField(
        upload_to="materials/media/course/images",
        verbose_name="Превью(картинка)",
        help_text="Вставьте превью курса",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание курса"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Название", help_text="Введите название урока"
    )
    image = models.ImageField(
        upload_to="materials/media/course/images",
        verbose_name="Превью(картинка)",
        help_text="Вставьте превью урока",
    )
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание урока"
    )
    video = models.URLField(
        verbose_name="Ссылка на видео", help_text="Вставьте ссылку на видео"
    )
    course = models.ForeignKey(
        to=Course,
        on_delete=models.CASCADE, related_name='lessons',
        verbose_name="Курс",
        help_text="Выберите курс",

    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
