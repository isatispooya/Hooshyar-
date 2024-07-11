from django.shortcuts import render
from rest_framework import status , generics
from . import models
from . import serializers
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from Authentication import fun
from Authentication.serializers import UserSerializer , ConsultantSerializer
from Stracture.serializers import SelectTimeSerializer
import pandas as pd
from persiantools.jdatetime import JalaliDate
from Authentication.models import Consultant


# georgia date to jalali
def date_to_jalali(date):
    return str(JalaliDate(date))

# id to time
def timefromid (id) :
    time = models.SelectTime.objects.filter(id=id).first()
    return time.time

# id to date 
def datefromid (id) :
    date =models.SelectTime.objects.filter(id=id).first()
    date = str(date_to_jalali(date.date))
    return date


# id to consultant's name/last name
def consultantfromid (id) :
    consultant = models.Consultant.objects.filter(id=id).first()
    serializer = ConsultantSerializer(consultant).data
    return [consultant.name + ' ' + consultant.last_name  ,serializer['profile_photo'] ]


# id to kind
def  kindfromid (id) :
    kind = models.KindOfCounseling.objects.filter(id=id).first()
    return kind.title


# id to user's name/last name
def userfromid (id) :
    user = models.Auth.objects.filter(id=id).first()
    return user.name + ' ' + user.last_name


# for questions
def questiontorisking (id):
    question = models.Question.objects.filter(id=id).first()
    serializer_question = serializers.QuestionSerializer(question).data
    print (serializer_question)

    risktaking = 0
    if serializer_question['question_1'] <35 :
        risktaking = risktaking + 1.5
    elif serializer_question['question_1'] <45 :
        risktaking = risktaking + 1
    elif serializer_question['question_1'] <55 :
        risktaking = risktaking + 0.5
    elif serializer_question['question_1'] <65 :
        risktaking = risktaking + 0
    elif serializer_question['question_1'] <75 :
        risktaking = risktaking  -0.5
    elif serializer_question['question_1'] >75 :
        risktaking = risktaking  -1

    risktaking = risktaking + int( serializer_question['question_2'])
    risktaking = risktaking + int(str( serializer_question['question_3']).replace('1', '0').replace('2', '1').replace('4', '5'))
    risktaking = risktaking + int(str( serializer_question['question_4']).replace('1', '5').replace('2', '3').replace('3', '1').replace('4', '0'))
    risktaking = risktaking + int(str( serializer_question['question_5']).replace('1', '0').replace('2', '1').replace('4', '5'))
    risktaking = risktaking + int(str( serializer_question['question_6']).replace('1', '5').replace('2', '3').replace('3', '1').replace('4', '0'))
    risktaking = risktaking + int(str( serializer_question['question_7']).replace('1', '0').replace('3', '4').replace('4', '6'))
    risktaking = risktaking + int(str( serializer_question['question_8']).replace('1', '0').replace('2', '1').replace('3', '2').replace('4', '3'))
    risktaking = risktaking + int(str( serializer_question['question_9']).replace('1', '0').replace('3', '4').replace('4', '6'))
    return [risktaking,serializer_question['question_10'],serializer_question['question_1']]


# user's age
def datebirthtoage (date) :
    date_now = datetime.datetime.now().date()
    age = date_now -date
    age = int (age.days/365.2425)
    return age



# visit for user  
class VisitViewset(APIView):

    # set visit
    def post(self, request):
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            user = user.first()  
            consultant = models.Consultant.objects.filter(id = request.data.get('consultant'))
            if not consultant.exists ():
                return Response('no consultant', status=status.HTTP_400_BAD_REQUEST)
            consultant = consultant.first()
            serializer_consultant = ConsultantSerializer(consultant)
            question = request.data.get('questions')
            question_model = models.Question(
                question_1 = datebirthtoage(user.date_birth) ,
                question_2 = question['1'] ,
                question_3 = question['2'] ,
                question_4 = question['3'] ,
                question_5 = question['4'] ,
                question_6 = question['5'] ,
                question_7 = question['6'] ,
                question_8 = question['7'] ,
                question_9 = question['8'] ,
                question_10 = question['9'] )
            question_model.save()
            serializer_question = serializers.QuestionSerializer(question_model)
            print(question_model.question_1)
            if question_model.question_1 < 18:
                return Response({'message': 'your age <18'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            kind = models.KindOfCounseling.objects.filter(id= request.data.get ('kind'))
            if not kind.exists() :
                return Response ('no kind', status=status.HTTP_400_BAD_REQUEST)
            kind = kind.first()
            serializer_kind = serializers.KindOfCounselingSerializer (kind)

            date_str = request.data.get('date')
            time = request.data.get ('time')
            if not date_str:
                return Response({'error': 'No date provided'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                date_str = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

            date = models.SelectTime.objects.filter(date =date_str , time =time , reserve = False ,consultant = consultant )
            if not date.exists () :
                return Response ({'maybe the date, time is booked or the time is not available for this consultant'}, status=status.HTTP_406_NOT_ACCEPTABLE)
           
            date = date.first()

            visit_model = models.Visit(customer=user , consultant =consultant  ,kind = kind, questions = question_model , date = date)

            visit_model.save()
            models.SelectTime.objects.filter(id=date.id).update(reserve=True)
            
            return Response({'message' : 'your visit set'}, status=status.HTTP_201_CREATED)

    # show visit for user
    def get(self, request):
    
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_instance = user.first()
        visits = models.Visit.objects.filter(customer=user_instance)
        
        if not visits.exists():
            return Response({'message' : 'The user does not have a visit'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.VisitSerializer(visits, many=True)

        df = pd.DataFrame(serializer.data)
        df['consultant'] = df ['consultant'].apply(consultantfromid)
        df['consultant_photo'] = [x[1] for x in df ['consultant']]
        df['consultant'] = [x[0] for x in df ['consultant']]
        df['time'] = df ['date'].apply(timefromid)
        df['date'] = df ['date'].apply(datefromid)
        df['kind'] = df ['kind'].apply(kindfromid)
        df['customer'] = df ['customer'].apply(userfromid)
        df = df.drop(columns='create_at')
        df['survey'] = df ['survey'].fillna(0)
        df['note'] = df ['note'].fillna('')
        df = df.to_dict('records')

        return Response(df, status=status.HTTP_200_OK)





# show visit list for consultant
class VisitConsultationsViewset (APIView) :
    def get(self ,request) :
        Authorization = request.headers['Authorization']
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        consultant_instance = fun.decryptionConsultant(Authorization).first()  
        if not consultant_instance:
            return Response({'error': 'Consultant not found'}, status=status.HTTP_404_NOT_FOUND)
        visit = models.Visit.objects.filter(consultant =consultant_instance)
        visit = [serializers.VisitSerializer(x).data for x in visit]
        df = pd.DataFrame(visit)
        print(df)
        df['consultant'] = df ['consultant'].apply(consultantfromid)
        df['consultant_photo'] = [x[1] for x in df ['consultant']]
        df['consultant'] = [x[0] for x in df ['consultant']]
        df ['customer'] = df['customer'].apply(userfromid)
        df ['kind'] = df['kind'].apply(kindfromid)
        df['time'] = df ['date'].apply(timefromid)
        df ['date'] = df['date'].apply(datefromid)
        df = df.drop(columns='create_at')
        df['survey'] = df['survey'].fillna(0)
        df['note'] = df['note'].fillna('')
        df =df.to_dict('records')
        return Response (df,status=status.HTTP_200_OK)
        

# show visit detail for consultant
class VisitConsultationsDetialViewset(APIView):
    def get(self,request ,id ) :
        Authorization = request.headers.get ('Authorization')
        if not Authorization :
            return Response({'error':'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        consultant = fun.decryptionConsultant(Authorization)
        if not consultant :
            return Response ({'error' : 'Consultant not found'} , status=status.HTTP_404_NOT_FOUND)
        consultant = consultant.first()
        visits = models.Visit.objects.filter(id = id)
        if not visits.exists():
            return Response({'message' : 'not found visit'}, status=status.HTTP_404_NOT_FOUND)
        
        serialized_visits = serializers.VisitSerializer(visits, many=True).data
        df = pd.DataFrame(serialized_visits)
        print(df)
        df['consultant'] = df ['consultant'].apply(consultantfromid)
        df['consultant_photo'] = [x[1] for x in df ['consultant']]
        df['consultant'] = [x[0] for x in df ['consultant']]
        df['customer'] = df ['customer'].apply(userfromid)
        df['kind'] = df ['kind'].apply(kindfromid)
        df['time'] = df ['date'].apply(timefromid)
        df['date'] = df ['date'].apply(datefromid)
        df = df.drop(columns='create_at')
        df ['survey'] = df['survey'].fillna (0)
        df ['note'] = df['note'].fillna('')
        df ['questions'] =df['questions'].apply(questiontorisking)
        df['risktaking'] =[x[0] for x in df['questions']]
        df['capital'] =[x[1] for x in df['questions']]
        df ['age'] = [x[2]for x in df ['questions']]
        df = df.drop(columns='questions')
        df = df.to_dict('records')[0]
        return Response(df, status=status.HTTP_200_OK)
    
    

# Question
'''
class QuestionViewset(APIView):
    def post (self, request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization :
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user :
            return Response({'error' : 'User not found'} , status=status.HTTP_404_NOT_FOUND)
        user_instance = user.first()
        data = request.data.copy()
        data ['title'] = user_instance.id 
        serializer = serializers.QuestionSerializer(data=data)
        if serializer.is_valid() :
            serializer.save()
            return Response (serializer.data , status=status.HTTP_201_CREATED)
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get (self, request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization :
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        user = fun.decryptionUser(Authorization)
        if not user :
            return Response({'error' : 'User not found'} , status=status.HTTP_404_NOT_FOUND)
        user_instance = user.first()
        question = models.Question.objects.all()
        if not question.exists () :
            return Response ([],status=status.HTTP_200_OK)
        serializer = serializers.QuestionSerializer(question , many = True)
        return Response (serializer.data , status=status.HTTP_200_OK)

'''







# Kind Of Counseling
class KindOfCounselingViewset(APIView):
    
    def get(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        kind = models.KindOfCounseling.objects.all()
        if not kind.exists():
            return Response([], status=status.HTTP_200_OK)
        
        serializer = serializers.KindOfCounselingSerializer(kind, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# card box for user
class CardBoxUserViewSet(APIView) :
    def get (self,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        print(user)
        visits = models.Visit.objects.filter(customer = user)
        number_visit = visits.count()
        consultant = models.Consultant.objects.all()
        number_consultant = consultant.count()
        active_visit = models.Visit.objects.filter(status = 'completing',customer = user )
        number_active_visit = active_visit.count()
        return Response({'visits' :number_visit  , 'all_consultants' :number_consultant , 'active_consultations' : number_active_visit} , status=status.HTTP_200_OK)
   

    

# card box for consultant
class CardBoxConsultantViewset (APIView) :
    def get (self,request) :
        Authorization = request.headers.get ('Authorization')
        if not Authorization :
            return Response({'error':'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        consultant = fun.decryptionConsultant(Authorization)
        if not consultant :
            return Response ({'error' : 'Consultant not found'} , status=status.HTTP_404_NOT_FOUND)
        consultant = consultant.first()        
        visits = models.Visit.objects.filter(consultant=consultant)
        number_visits = visits.count()
        active_visit = models.Visit.objects.filter(status = 'completing',consultant=consultant)
        number_active_visit = active_visit.count()
        consultant_score = consultant.rank

        return Response({'visits' : number_visits , 'consultations_waiting' : number_active_visit ,'Consultant_score' :consultant_score } , status=status.HTTP_200_OK )


# show consultant profile for customer
class ConsultantProfileForuserViewset (APIView) :
    def get (self,request, id) :
        Authorization = request.headers['Authorization']
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user = user.first()
        consultant = models.Consultant.objects.filter(id = id).first()
        serializer_consultant = ConsultantSerializer(consultant).data
        return Response (serializer_consultant , status=status.HTTP_200_OK)
