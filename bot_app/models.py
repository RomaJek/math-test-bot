from django.db import models

class BotUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=255, verbose_name="F.I.O")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dizimnen ótken waqtı")

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Bot paydalanıwshısı"
        verbose_name_plural = "Bot paydalanıwshıları"


class Question(models.Model):
    ANSWER_CHOICES = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
    ]
    text = models.TextField(verbose_name="Soraw teksti")
    image = models.ImageField(upload_to='questions/', null=True, blank=True, verbose_name="Soraw súwreti")
    option_a = models.CharField(max_length=255, verbose_name="A variantı")
    option_b = models.CharField(max_length=255, verbose_name="B variantı")
    option_c = models.CharField(max_length=255, verbose_name="C variantı")
    option_d = models.CharField(max_length=255, verbose_name="D variantı")
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES, verbose_name="Durıs juwap")
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    def __str__(self):
        return f"Soraw: {self.text[:50]}..."

    class Meta:
        verbose_name = "Soraw"
        verbose_name_plural = "Sorawlar"


class TestAttempt(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='attempts', verbose_name="Oqıwshı")
    score = models.IntegerField(verbose_name="Toplanǵan ball")
    total_questions = models.IntegerField(default=10, verbose_name="Ulıwma sorawlar sanı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tapsırılǵan waqıt")

    def __str__(self):
        return f"{self.user.full_name} - {self.score}/{self.total_questions}"

    class Meta:
        verbose_name = "Test nátiyjesi"
        verbose_name_plural = "Test nátiyjeleri"


class AttemptDetail(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='details', verbose_name="Test")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Soraw")
    user_answer = models.CharField(max_length=1, verbose_name="Oqıwshı juvabı")
    is_correct = models.BooleanField(verbose_name="Durıs pa?")

    def __str__(self):
        return f"Detallar: {self.attempt.user.full_name}"


class BotState(models.Model):
    user_id = models.BigIntegerField(unique=True, verbose_name="User ID")
    state = models.CharField(max_length=255, null=True, blank=True)
    data = models.JSONField(default=dict, verbose_name="FSM Data")

    def __str__(self):
        return f"State: {self.user_id} - {self.state}"


