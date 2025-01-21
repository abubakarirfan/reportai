from django.test import TestCase
from django.contrib.auth.models import User
from .models import MedicalReport


class ReportAccessTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='testpass')
        self.user2 = User.objects.create_user(
            username='user2', password='testpass')
        self.report = MedicalReport.objects.create(
            user=self.user1, image='test.jpg')

    def test_report_list_restricts_to_user(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get('/reports/list/')
        # User1 can see their own report
        self.assertContains(response, 'test.jpg')

        self.client.login(username='user2', password='testpass')
        response = self.client.get('/reports/list/')
        # User2 cannot see User1's report
        self.assertNotContains(response, 'test.jpg')

    def test_report_detail_restricts_to_user(self):
        self.client.login(username='user1', password='testpass')
        response = self.client.get(f'/reports/{self.report.pk}/')
        # User1 can access their report
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user2', password='testpass')
        response = self.client.get(f'/reports/{self.report.pk}/')
        self.assertEqual(response.status_code, 403)  # User2 gets Forbidden
