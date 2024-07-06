from django.shortcuts import render
from rest_framework import status , generics
from . import models
from . import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from Authentication import fun
import pandas as pd
from .fun import groupingTime
from persiantools.jdatetime import JalaliDate
from datetime import datetime
import pytz

def date_str_to(date):
    return datetime.strptime(date,"%Y-%m-%d")

def date_to_jalali(date):
    return str(JalaliDate(date))

def date_to_weekday(date):
    return date.weekday()


class SelectTimeUserViewset(APIView):
    def get(self, request, pk):
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            times = models.SelectTime.objects.filter(consultant_id=pk).order_by('date', 'time' , 'reserve')
            if not times.exists():
                return Response([], status=status.HTTP_200_OK)
            df = [serializers.SelectTimeSerializer(x).data for x in times]
            df = pd.DataFrame(df)
            df = df.groupby('date').apply(groupingTime)
            df = df.reset_index()
            df = df[['date','time']]
            df['date'] = df['date'].apply(date_str_to)
            df['jalali'] = df['date'].apply(date_to_jalali)
            df['weekday'] = df['date'].apply(date_to_weekday)
            df = df.to_dict('records')
            return Response(df, status=status.HTTP_200_OK)
    





class SelectTimeConsultantViewset(APIView):
    def get(self, request):
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

            consultant = fun.decryptionConsultant(Authorization).first()
            if not consultant:
                return Response({'error': 'consultant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            times = models.SelectTime.objects.all().order_by('date', 'time' , 'reserve')
            if not times.exists():
                return Response([], status=status.HTTP_200_OK)
            df = [serializers.SelectTimeSerializer(x).data for x in times]
            df = pd.DataFrame(df)
            df = df.groupby('date').apply(groupingTime)
            df = df.reset_index()
            print(df)
            df = df[['date','time']]
            df['date'] = df['date'].apply(date_str_to)
            df['jalali'] = df['date'].apply(date_to_jalali)
            df['weekday'] = df['date'].apply(date_to_weekday)
            df = df.to_dict('records')
            return Response(df, status=status.HTTP_200_OK)
    


class SetTimeConsultant (APIView) :
        def post (self , request) :
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

            consultant = fun.decryptionConsultant(Authorization).first()
            if not consultant:
                return Response({'error': 'consultant not found'}, status=status.HTTP_404_NOT_FOUND)
            
            time_stamp = request.data.get ('date')
            print(time_stamp)
            if not time_stamp :
                 return Response({'message' : 'no date'} , status=status.HTTP_404_NOT_FOUND)
            time_stamp = int (time_stamp)/1000
            time_stamp = time_stamp = datetime.fromtimestamp(time_stamp)
            date = time_stamp.date()
            time = time_stamp.hour
            set_date = models.SelectTime.objects.filter(date=date ,time=time)
            if set_date.exists () :
                 return Response ({'message' : 'این تاریخ از قبل تعین شده است'} , status=status.HTTP_406_NOT_ACCEPTABLE)
            set_time_model = models.SelectTime (consultant=consultant , date =date , time = time)
            set_time_model.save()

            return Response ({'message' : 'زمان مشاوره ثبت شد'},status=status.HTTP_200_OK)
