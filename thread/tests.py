from rest_framework import test, status
from .models import Answer, Question
from django.urls import reverse
from users.models import User
import logging


logger = logging.getLogger(__name__)


class QuestionTest(test.APITestCase):
    
    api_client = test.APIClient()

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='test user1', email='test22323@test.com', password='m12457896')

        user2 = User.objects.create_user(username='test user2', email='test2@test.com', password='m12457896')

        question = Question.objects.create(title='test', body='test body', owner=user1)

        Answer.objects.create(content='test body answer', question=question, owner=user2)

    def setUp(self):
        self.question = Question.objects.get(id=1)
        self.answer = Answer.objects.get(id=1)

    def user_login(self, pk):
        user = User.objects.get(id=pk)
        return self.api_client.force_authenticate(user=user)

    def test_create_question(self):

        url = reverse('question')
        data = {'title': 'masood', 'body': 'some body content', 'tags': [{'name': 'test'}, {'name': 'kir'}]}

        self.user_login(pk=1)
        response = self.api_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_question_list(self):
        url = reverse('question')
        response = self.api_client.get(url, {'search': 'test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_question_detail(self):
        response = self.client.get(self.question.get_absolute_url(), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.question.title)

    def test_question_update(self):

        url = reverse('question-detail', kwargs={'slug': self.question.slug})
        
        data = {'title': 'test update', 'body': 'body test 2', 'slug': 'test-update'}

        user = User.objects.get(id=2)
        self.api_client.force_authenticate(user)
        response2 = self.api_client.put(url, data)

        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        self.user_login(1)
        response = self.api_client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['title'], self.question.title)

    def test_question_delete(self):

        self.user_login(1)
        url = reverse('question-detail', kwargs={'slug': self.question.slug})
        response = self.api_client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_answer_create(self):
        url = reverse('answer-create')
        data = {'content': 'answer content', 'question': self.question.id}
        self.user_login(pk=2)
        response = self.api_client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_answer_update(self):

        data = {'content': 'body test answer update'}

        self.user_login(1)
        response1 = self.api_client.put(self.answer.get_absolute_url(), data)
        self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)

        self.user_login(2)
        response2 = self.api_client.put(self.answer.get_absolute_url(), data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response2.data.get('content'), self.answer.content)

    def test_answer_delete(self):

        self.user_login(2)
        response = self.api_client.delete(self.answer.get_absolute_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_best_answer(self):

        self.user_login(1)
        data = {'best_answer': self.answer.id}

        response = self.api_client.patch(self.question.get_absolute_url(), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.answer.owner.point, 0)

    def test_vote_to_answer(self):
        url = reverse('vote')
        data = {'answer': self.answer.id, 'value': 1}

        self.user_login(1)
        response = self.api_client.post(url, data)

        response_2 = self.api_client.post(url, data)  # check for voting by same user again

        self.user_login(self.answer.owner_id)
        response_3 = self.api_client.post(url, data)  # check for voting by answer owner himself

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_3.status_code, status.HTTP_400_BAD_REQUEST)
