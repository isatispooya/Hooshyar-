from rest_framework import serializers
from . import models  
from rest_framework import serializers
from Stracture.serializers import SelectTimeSerializer
from Authentication.serializers import ConsultantSerializer




class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = '__all__'   

class VisitSerializer(serializers.ModelSerializer):
    consultant = ConsultantSerializer()
    customer = serializers.PrimaryKeyRelatedField(queryset=models.Auth.objects.all())
    questions = serializers.PrimaryKeyRelatedField(queryset=models.Question.objects.all())


    class Meta:
        model = models.Visit
        fields = '__all__'   



class KindOfCounselingSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = models.KindOfCounseling
        fields = '__all__'   

