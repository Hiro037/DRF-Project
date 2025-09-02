from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from materials.models import Course, Lesson
from users.models import Subscription
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Функция для создания тестового изображения
def create_test_image():
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile('test_image.jpg', file.getvalue(), content_type='image/jpeg')

class LessonAndSubscriptionTests(TestCase):
    def setUp(self):
        # Создаем клиента для запросов
        self.client = APIClient()

        # Создаем группу модераторов
        self.moderator_group = Group.objects.create(name='moderator')

        # Создаем пользователей
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        self.owner_user = User.objects.create_user(
            email='owner@example.com',
            password='owner123'
        )
        self.moderator_user = User.objects.create_user(
            email='moderator@example.com',
            password='moderator123'
        )
        self.moderator_user.groups.add(self.moderator_group)
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='user123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Course Description',
            owner=self.owner_user,
            price=100.00,
            image=create_test_image()
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video='https://youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner_user,
            price=50.00,
            image=create_test_image()
        )

        # URL для запросов
        self.lesson_list_url = reverse('materials:lesson-list')
        self.lesson_detail_url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.pk})
        self.subscribe_url = reverse('users:subscribe')
        self.course_detail_url = reverse('materials:course-detail', kwargs={'pk': self.course.pk})

    # Тесты для уроков

    def test_create_lesson_as_admin(self):
        """Проверяем, что админ может создать урок"""
        self.client.force_authenticate(user=self.admin_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.admin_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().title, 'New Lesson')

    def test_create_lesson_as_owner(self):
        """Проверяем, что владелец курса может создать урок"""
        self.client.force_authenticate(user=self.owner_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().title, 'New Lesson')

    def test_create_lesson_as_moderator(self):
        """Проверяем, что модератор НЕ может создать урок"""
        self.client.force_authenticate(user=self.moderator_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.moderator_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_as_regular_user(self):
        """Проверяем, что обычный пользователь может создать урок"""
        self.client.force_authenticate(user=self.regular_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.regular_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().title, 'New Lesson')

    def test_create_lesson_with_invalid_video_link(self):
        """Проверяем, что нельзя создать урок с неверной ссылкой"""
        self.client.force_authenticate(user=self.admin_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://vimeo.com/new_video',
            'course': self.course.id,
            'owner': self.admin_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lesson_with_external_link_in_description(self):
        """Проверяем, что нельзя создать урок с внешней ссылкой в описании"""
        self.client.force_authenticate(user=self.admin_user)
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'Visit https://invalid.com for more info',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.admin_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lesson_empty_title(self):
        """Проверяем, что нельзя создать урок с пустым названием"""
        self.client.force_authenticate(user=self.admin_user)
        image = create_test_image()
        data = {
            'title': '',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.admin_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_lesson_unauthenticated(self):
        """Проверяем, что нельзя создать урок без авторизации"""
        image = create_test_image()
        data = {
            'title': 'New Lesson',
            'description': 'New Lesson Description',
            'image': image,
            'video': 'https://youtube.com/watch?v=new_video',
            'course': self.course.id,
            'owner': self.admin_user.id,
            'price': 50.0
        }
        response = self.client.post(self.lesson_list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lesson_as_moderator(self):
        """Проверяем, что модератор может посмотреть урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.lesson.title)

    def test_retrieve_lesson_unauthenticated(self):
        """Проверяем, что без авторизации нельзя посмотреть урок"""
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_lesson_as_admin(self):
        """Проверяем, что админ НЕ может обновить урок"""
        self.client.force_authenticate(user=self.admin_user)
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://youtube.com/watch?v=updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_as_owner(self):
        """Проверяем, что владелец урока может обновить урок"""
        self.client.force_authenticate(user=self.owner_user)
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://youtube.com/watch?v=updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_update_lesson_as_moderator(self):
        """Проверяем, что модератор может обновить урок"""
        self.client.force_authenticate(user=self.moderator_user)
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://youtube.com/watch?v=updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_update_lesson_as_regular_user(self):
        """Проверяем, что обычный пользователь НЕ может обновить урок"""
        self.client.force_authenticate(user=self.regular_user)
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://youtube.com/watch?v=updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_with_invalid_video_link(self):
        """Проверяем, что нельзя обновить урок с неверной ссылкой"""
        self.client.force_authenticate(user=self.owner_user)
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://vimeo.com/updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_lesson_unauthenticated(self):
        """Проверяем, что без авторизации нельзя обновить урок"""
        image = create_test_image()
        data = {
            'title': 'Updated Lesson',
            'description': self.lesson.description,
            'image': image,
            'video': 'https://youtube.com/watch?v=updated_video',
            'course': self.course.id,
            'owner': self.owner_user.id,
            'price': 50.0
        }
        response = self.client.put(self.lesson_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_lesson_as_admin(self):
        """Проверяем, что админ НЕ может удалить урок"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_owner(self):
        """Проверяем, что владелец урока может удалить урок"""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_as_moderator(self):
        """Проверяем, что модератор НЕ может удалить урок"""
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_as_regular_user(self):
        """Проверяем, что обычный пользователь НЕ может удалить урок"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_unauthenticated(self):
        """Проверяем, что без авторизации нельзя удалить урок"""
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_to_course(self):
        """Проверяем, что пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.regular_user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Проверяем, что пользователь может отписаться от курса"""
        Subscription.objects.create(user=self.regular_user, course=self.course)
        self.client.force_authenticate(user=self.regular_user)
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.regular_user, course=self.course).exists())

    def test_subscribe_unauthenticated(self):
        """Проверяем, что без авторизации нельзя подписаться"""
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_to_nonexistent_course(self):
        """Проверяем, что нельзя подписаться на несуществующий курс"""
        self.client.force_authenticate(user=self.regular_user)
        data = {'course_id': 9999}
        response = self.client.post(self.subscribe_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_subscription_status(self):
        """Проверяем, что статус подписки отображается в данных курса"""
        Subscription.objects.create(user=self.moderator_user, course=self.course)
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_course_subscription_status_unauthenticated(self):
        """Проверяем, что без авторизации нельзя посмотреть курс"""
        Subscription.objects.create(user=self.regular_user, course=self.course)
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)