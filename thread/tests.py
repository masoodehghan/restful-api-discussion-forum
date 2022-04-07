from rest_framework import test, status
from .models import Answer, Question, Tag
from django.urls import reverse
from users.models import User

class QuestionTest(test.APITestCase):
    
    api_client = test.APIClient()
    
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create_user(email='ali@test.com', password='m12457896')
        self.user_2 = User.objects.create_user(email='test@test.com', password='m12457896')
        self.tag = Tag.objects.create(name='Test Tag', slug='test-tag')
        self.question = Question.objects.create(title='test', body='test body', owner=self.user)
        self.question.tags.add(self.tag)
        self.answer = Answer.objects.create(content='test body answer', question=self.question, owner=self.user_2)
        
        

    # it is part of test setup
    def login_with_token(self, user):
        
        url = reverse('token_obtain_pair')
        token = self.client.post(url,
                                {'email':user.email, 'password':'m12457896'},
                                format='json')

        return token.data['access']
       
    def test_create_question(self):
        
        url = reverse('question-create')
        token = self.login_with_token(self.user)
        data = {'title':'masdood', 'body':self.question.body}
        
        self.api_client.force_authenticate(self.user, token=token)
        response = self.api_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_question_list(self):
        url = reverse('question-list')
        response = self.client.get(url, {'q':'tag'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], self.question.title)
        
    def test_question_detail(self):
        question = self.question
        url = reverse('question-detail', kwargs={'slug':question.slug})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], question.title)
        
    def test_question_update(self):
        question = self.question
        url = reverse('question-detail', kwargs={'slug':question.slug})
        data = {'title': 'test update', 'body':'body test 2', 'slug':'test-update'}
        token = self.login_with_token(self.user)
        self.api_client.force_authenticate(user=self.user, token=token)
        response = self.api_client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['title'], question.title)
        
    def test_question_delete(self):
        
        question = self.question
        token = self.login_with_token(self.user)
        self.api_client.force_authenticate(user=self.user, token=token)
        
        url = reverse('question-detail', kwargs={'slug':question.slug})
        response = self.api_client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)    
    
    def test_answer_create(self):
        answer = self.answer
        answer.owner = self.user_2
        token = self.login_with_token(self.user_2)
        url = reverse('answer-create', kwargs={'slug':self.question.slug})
        self.api_client.force_authenticate(user=self.user_2, token=token)
        data = {'content':answer.content}
        response = self.api_client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_answer_update(self):
        token = self.login_with_token(self.user_2)
        url = reverse('answer-detail', kwargs={'pk':self.answer.id})
        self.api_client.force_authenticate(user=self.user_2, token=token)
        data = {'content':'body test answer update'}
        response = self.api_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('data').get('content'), self.answer.content)

    def test_answer_delete(self):
        token = self.login_with_token(self.user_2)
        url = reverse('answer-detail', kwargs={'pk':self.answer.id})
        self.api_client.force_authenticate(user=self.user_2, token=token)
        response = self.api_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_best_answer(self):
        token = self.login_with_token(self.user)
        url = reverse('best-answer', kwargs={'slug':self.question.slug, 'answer_pk':self.answer.id})
        self.api_client.force_authenticate(self.user, token)
        response = self.api_client.put(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'best answer submited')
        
        