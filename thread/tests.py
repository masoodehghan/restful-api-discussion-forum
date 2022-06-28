from rest_framework import test, status
from .models import Answer, Question, Tag
from django.urls import reverse
from users.models import User


class QuestionTest(test.APITestCase):
    
    api_client = test.APIClient()

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='test user1', email='test@test.com', password='m12457896')
        user1.save()

        user2 = User.objects.create_user(username='test user2', password='m12457896')
        user2.save()

        tag = Tag.objects.create(name='Test Tag')
        tag.save()
        question = Question.objects.create(title='test', body='test body', owner=user1)
        question.save()
        question.tags.add(tag)

        answer = Answer.objects.create(content='test body answer', question=question, owner=user2)
        answer.save()

    def user_login(self, pk):
        user = User.objects.get(id=pk)
        return self.api_client.force_authenticate(user=user)

    def test_create_question(self):

        url = reverse('question')
        data = {'title': 'masood', 'body': 'some body content'}

        self.user_login(pk=1)
        response = self.api_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_question_list(self):
        url = reverse('question')
        response = self.client.get(url, {'search': 'tag'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'test')

    def test_question_detail(self):
        question = Question.objects.get(id=1)

        # url = reverse('question-detail', kwargs={'slug': question.slug})
        response = self.client.get(question.get_absolute_url(), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], question.title)

    def test_question_update(self):
        question = Question.objects.get(id=1)
        url = reverse('question-detail', kwargs={'slug': question.slug})
        data = {'title': 'test update', 'body': 'body test 2', 'slug': 'test-update'}

        user = User.objects.get(id=2)
        self.api_client.force_authenticate(user)
        response2 = self.api_client.put(url, data)

        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        self.user_login(1)
        response = self.api_client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['title'], question.title)

    def test_question_delete(self):
        question = Question.objects.get(id=1)

        self.user_login(1)
        url = reverse('question-detail', kwargs={'slug': question.slug})
        response = self.api_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_answer_create(self):
        url = reverse('answer-create')
        data = {'content': 'answer content', 'question': 1}
        self.user_login(pk=2)
        response = self.api_client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_answer_update(self):
        answer = Answer.objects.get(id=1)
        # url = reverse('answer-detail', kwargs={'pk': answer.id})
        data = {'content': 'body test answer update'}

        self.user_login(1)
        response1 = self.api_client.put(answer.get_absolute_url(), data)
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

        self.user_login(2)
        response2 = self.api_client.put(answer.get_absolute_url(), data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response2.data.get('content'), answer.content)

    def test_answer_delete(self):
        answer = Answer.objects.get(id=1)
        self.user_login(2)
        response = self.api_client.delete(answer.get_absolute_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_best_answer(self):
        question = Question.objects.get(id=1)

        self.user_login(1)
        data = {'best_answer_id': 1}

        response = self.api_client.patch(question.get_absolute_url(), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

