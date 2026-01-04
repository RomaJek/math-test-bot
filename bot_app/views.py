import django_filters
from rest_framework import viewsets
from .models import BotUser, Question, TestAttempt
from .serializers import BotUserSerializer, QuestionSerializer, TestAttemptSerializer

import zipfile
import io
import openpyxl
from django.db import transaction
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

# --- 1. ARNALLI FILTIRLEW KLASSI ---
# Bul klass bazadan súwreti bar yamasa joq sorawlardı ajıratıw ushın kerek
class QuestionFilter(django_filters.FilterSet):
    # has_image=true yamasa false dep soraw jiberiw imkaniyatı
    has_image = django_filters.BooleanFilter(
        field_name='image', 
        method='filter_has_image', 
        label="Súwreti bar sorawlar"
    )

    class Meta:
        model = Question
        # Tiykarǵı filtrler
        fields = ['is_active', 'correct_answer']

    def filter_has_image(self, queryset, name, value):
        if value: # Eger true bolsa, súwreti bar (bos emes) sorawlar
            return queryset.exclude(image='')
        # Eger false bolsa, súwreti joq sorawlar
        return queryset.filter(image='')


# --- 2. VIEWSETS (API Logikası) ---

# TZ 4.2: Sorawlar CRUD API
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    # Biz jazǵan arnawlı filtir klassın qollanamız
    filterset_class = QuestionFilter
    
    # Tekst boyınsha izlew imkaniyatı
    search_fields = ['text']


# TZ 4.4: Paydalanıwshılar API (Tek kóriw ushın)
class BotUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BotUser.objects.all().order_by('-created_at')
    serializer_class = BotUserSerializer


# TZ 4.4: Test nátiyjeleri API (Tek kóriw ushın)
class TestAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TestAttempt.objects.all().order_by('-created_at')
    serializer_class = TestAttemptSerializer





# TZ 4.3: Excel + Súwretlerdi (ZIP) júklew API
class ZipImportView(APIView):
    # API-ge fayl qabıllaw imkaniyatın beremiz
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # 1. ZIP fayldı alıw hám tekseriw
        file_obj = request.FILES.get('file')
        if not file_obj or not file_obj.name.endswith('.zip'):
            return Response({"error": "Iltimas, .zip formatındaǵı arxiv júkleń!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ZIP-ti yadqa (RAM) júkleymiz
            with zipfile.ZipFile(io.BytesIO(file_obj.read())) as z:
                
                # Arxiv ishinen Excel (.xlsx) faylın tawabız
                excel_filename = next((f for f in z.namelist() if f.endswith('.xlsx')), None)
                if not excel_filename:
                    return Response({"error": "ZIP ishinde Excel (.xlsx) tabılmadı!"}, status=status.HTTP_400_BAD_REQUEST)

                # Excel-di ashamız
                with z.open(excel_filename) as excel_file:
                    workbook = openpyxl.load_workbook(excel_file)
                    sheet = workbook.active
                    
                    questions_created_count = 0
                    
                    # Tranzakciya baslaymız: bári saqlansın yamasa hesh nárse saqlanbasın
                    with transaction.atomic():
                        # Excel-di qatarma-qatar oqıymız (2-qatardan baslap)
                        for row in sheet.iter_rows(min_row=2, values_only=True):
                            if not row[0]: continue # Soraw teksti joq bolsa ótkerip jiberiw

                            # Jańa soraw obyektin tayarlaymız
                            new_q = Question(
                                text=row[0],
                                option_a=row[1],
                                option_b=row[2],
                                option_c=row[3],
                                option_d=row[4],
                                correct_answer=str(row[5]).lower().strip(),
                                is_active=True
                            )

                            # Eger 7-baganada (G column) súwret atı jazılǵan bolsa
                            image_name = row[6]
                            if image_name:
                                try:
                                    # ZIP-ten sol súwretti tawabız
                                    with z.open(image_name) as img_file:
                                        img_content = ContentFile(img_file.read())
                                        # Súwretti modelge biriktiremiz
                                        new_q.image.save(image_name, img_content, save=False)
                                except KeyError:
                                    # Súwret atı Excel-de bar, biraq ZIP-tiń ishinde joq bolsa - súwretsiz qosıla beredi
                                    pass

                            # Sorawdı bazaǵa saqlaw
                            new_q.save()
                            questions_created_count += 1

            return Response({
                "message": f"Áwmetli tamamlandı! {questions_created_count} dana soraw qosıldı."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Qáte júz berdi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



