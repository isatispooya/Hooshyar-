from django.db import models
from django.utils import timezone
from Authentication.models import Auth, Consultant
from Stracture.models import SelectTime
from django_summernote.fields import SummernoteTextField

class Question(models.Model):
    question_choices = [
        (1,'a'),
        (2,'b'),
        (3,'c'),
        (4,'d'),
        (5,'e'),
        (6,'f'),
        (7,'g'),
        (8,'h'),
        (9,'j'),
        (10,'k'),
    ]
    question_1 = models.IntegerField()
    question_2 = models.IntegerField(choices=question_choices)
    question_3 = models.IntegerField(choices=question_choices)
    question_4 = models.IntegerField(choices=question_choices)
    question_5 = models.IntegerField(choices=question_choices)
    question_6 = models.IntegerField(choices=question_choices)
    question_7 = models.IntegerField(choices=question_choices)
    question_8 = models.IntegerField(choices=question_choices)
    question_9 = models.IntegerField(choices=question_choices)
    question_10 = models.IntegerField(choices=question_choices)

class KindOfCounseling(models.Model):
    title = models.CharField(max_length=100 , unique= True)
    price = models.IntegerField()
    icon = models.ImageField(upload_to='Static/images/' , blank=True, null=True)


class Visit(models.Model):
    customer = models.ForeignKey(Auth, on_delete=models.CASCADE)
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    questions = models.ForeignKey(Question, on_delete=models.CASCADE)
    create_at = models.DateTimeField(default=timezone.now)
    # cost = models.IntegerField()
    kind = models.ForeignKey(KindOfCounseling ,on_delete=models.CASCADE ) 
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    survey = models.IntegerField(choices=RATING_CHOICES , null=True , blank= True)
    # invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    note = models.CharField( max_length=2000 , null=True , blank= True)
    OPTION_Status = [
        ('completing', 'completing'),
        ('waiting', 'waiting'),
        ('done', 'done'),
        ('cancel', 'cancel'),
    ]
    status = models.CharField(max_length=20, choices=OPTION_Status , default='completing')
    date = models.ForeignKey(SelectTime , on_delete=models.CASCADE)
    

    def __str__(self):
        return f'{self.customer} - {self.consultant}'
