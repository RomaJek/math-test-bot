from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, BotUserViewSet, TestAttemptViewSet, ZipImportView, DashboardView

# Router — barlıq CRUD mánzillerin (GET, POST, PUT, DELETE) avtomat jaratadı
router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'users', BotUserViewSet)
router.register(r'attempts', TestAttemptViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Zip import manzili
    path('import-questions/', ZipImportView.as_view(), name='import-questions'),
    path('dashboard/', DashboardView.as_view(), name='admin-dashboard'),
]
