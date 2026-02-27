"""
Tests for the MyHealth AI backend.
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class UserAuthTestCase(APITestCase):
    """Tests for user registration and authentication."""

    def test_user_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        User.objects.create_user(email='login@example.com', password='TestPass123!')
        data = {'email': 'login@example.com', 'password': 'TestPass123!'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_registration_password_mismatch(self):
        data = {
            'email': 'mismatch@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'WrongPass!',
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SymptomAnalysisTestCase(APITestCase):
    """Tests for symptom analysis endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(email='symptom@example.com', password='TestPass123!')
        self.client.force_authenticate(user=self.user)

    def test_symptom_analysis(self):
        data = {'symptom_text': 'I have chest pain and shortness of breath'}
        response = self.client.post('/api/symptom/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('classification', response.data)
        self.assertIn('risk_level', response.data)
        self.assertIn('rag_response', response.data)

    def test_symptom_analysis_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {'symptom_text': 'I have a headache'}
        response = self.client.post('/api/symptom/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_symptom_text_too_short(self):
        data = {'symptom_text': 'hi'}
        response = self.client.post('/api/symptom/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmergencyDetectionTestCase(APITestCase):
    """Tests for emergency detection endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(email='emergency@example.com', password='TestPass123!')
        self.client.force_authenticate(user=self.user)

    def test_critical_emergency_detection(self):
        data = {'symptom_text': 'I am having a heart attack, severe chest pain'}
        response = self.client.post('/api/emergency/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['severity'], 'CRITICAL')

    def test_low_severity_symptoms(self):
        data = {'symptom_text': 'I have a mild runny nose today'}
        response = self.client.post('/api/emergency/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['severity'], 'LOW')


class RecommendationTestCase(APITestCase):
    """Tests for recommendation endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(email='recommend@example.com', password='TestPass123!')
        self.client.force_authenticate(user=self.user)

    def test_recommendation_without_analysis(self):
        response = self.client.get('/api/recommend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recommendation_with_analysis(self):
        # First create a symptom analysis
        symptom_response = self.client.post('/api/symptom/', {
            'symptom_text': 'I have been experiencing chest pain and high blood pressure'
        })
        self.assertEqual(symptom_response.status_code, status.HTTP_200_OK)
        analysis_id = symptom_response.data['analysis_id']

        # Get recommendations
        response = self.client.get(f'/api/recommend/?analysis_id={analysis_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('diet', response.data)
        self.assertIn('specialist', response.data)


class ClassifierTestCase(TestCase):
    """Unit tests for the symptom classifier."""

    def test_cardiovascular_classification(self):
        from ml_engine.classifier import get_classifier
        classifier = get_classifier()
        category, confidence, risk_level = classifier.classify('chest pain shortness of breath palpitations')
        self.assertEqual(category, 'cardiovascular')

    def test_respiratory_classification(self):
        from ml_engine.classifier import get_classifier
        classifier = get_classifier()
        category, confidence, risk_level = classifier.classify('cough wheezing asthma breathing difficulty')
        self.assertEqual(category, 'respiratory')

    def test_emergency_risk_level(self):
        from ml_engine.classifier import get_classifier
        classifier = get_classifier()
        _, _, risk_level = classifier.classify('chest pain heart attack severe')
        self.assertEqual(risk_level, 'CRITICAL')

    def test_low_risk_level(self):
        from ml_engine.classifier import get_classifier
        classifier = get_classifier()
        _, _, risk_level = classifier.classify('mild headache today')
        self.assertEqual(risk_level, 'LOW')


class EmergencyDetectorTestCase(TestCase):
    """Unit tests for the emergency detector."""

    def test_critical_detection(self):
        from emergency.detector import detect_emergency
        result = detect_emergency('I cannot breathe and having chest pain')
        self.assertEqual(result['severity'], 'CRITICAL')

    def test_mental_health_crisis(self):
        from emergency.detector import detect_emergency
        result = detect_emergency('I feel suicidal and hopeless')
        self.assertEqual(result['severity'], 'CRITICAL')
        self.assertEqual(result['emergency_contact'], '988')

    def test_low_severity(self):
        from emergency.detector import detect_emergency
        result = detect_emergency('I have a mild cold today with slight runny nose')
        self.assertEqual(result['severity'], 'LOW')


class RAGSystemTestCase(TestCase):
    """Unit tests for the RAG system."""

    def test_retrieval(self):
        from ml_engine.rag import get_rag_system
        rag = get_rag_system()
        results = rag.retrieve('chest pain heart disease', top_k=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_response_generation(self):
        from ml_engine.rag import get_rag_system
        rag = get_rag_system()
        result = rag.generate_response('What should I do for high blood pressure?')
        self.assertIn('response', result)
        self.assertIn('sources', result)


class RecommendationEngineTestCase(TestCase):
    """Unit tests for recommendation engine."""

    def test_cardiovascular_recommendations(self):
        from recommendations.engine import get_recommendations
        recs = get_recommendations('cardiovascular', 'HIGH')
        self.assertIn('diet', recs)
        self.assertIn('exercise', recs)
        self.assertIn('specialist', recs)
        self.assertEqual(recs['specialist'], 'Cardiologist')
        self.assertIn('HIGH PRIORITY', recs['notes'])

    def test_critical_risk_note(self):
        from recommendations.engine import get_recommendations
        recs = get_recommendations('cardiovascular', 'CRITICAL')
        self.assertIn('URGENT', recs['notes'])
