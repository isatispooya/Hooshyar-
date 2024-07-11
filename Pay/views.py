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
from Visit.models import KindOfCounseling
from Visit.serializers import KindOfCounselingSerializer


# show invoice before buy
class PayViewset(APIView):
    def get(self, request, kind ):
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            code = request.query_params.get('code')
            
            kindofcounseling = KindOfCounseling.objects.filter(id=kind).first()
            serializer_kindofcounseling = KindOfCounselingSerializer(kindofcounseling)
            result = {'price' :int (serializer_kindofcounseling.data['price'])}

            off = 0
            try :
                 
                discount = models.Discount.objects.filter(code=code).first()
                serializer_discount= serializers.DiscountSerializer(discount)

                expire_discount = serializer_discount.data ['expiration_date']
                expire_discount =datetime.datetime.strptime (serializer_discount.data ['expiration_date'] , "%Y-%m-%dT%H:%M:%SZ").date()
                now = datetime.datetime.now().date()

                serializer_discount= serializers.DiscountSerializer(discount)
                number_of_times = serializer_discount.data['number_of_times']


                    # فعلا تعداد دفعات بیشتر از 0  میزاریم بعدش درست میکنیم
                        
                if number_of_times > 0 and discount :
                    
                    if expire_discount >  now  :

                        if serializer_discount.data['kind'] == 'per' :
                            per = int(serializer_discount.data ['amount'])/100
                            per = min (1,per)
                            off= int (per * result['price'])
                        else :
                            value = int(serializer_discount.data ['amount'])
                            off = min(value , result['price'])
            except :
                pass

            result ['off']= off
            result['final_price'] = result['price'] - off
            result['tax'] = int (result ['final_price'] * 0.1)
            result['pey'] = int(result['final_price'] + result ['tax'])
            return Response(result, status=status.HTTP_200_OK)           
    


# show and check discount code
class DiscountViewset (APIView) :
    def get (self ,request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        code_discount = request.data.get('code')
        if not code_discount :
            return Response ({'message' : 'کد تخفیف را وراد کنید'},status=status.HTTP_406_NOT_ACCEPTABLE)
        code_check = models.Discount.objects.filter(code = code_discount).first()
        if not code_check  :
            return Response ({'message' : 'کد تخفیف معتبر نیست'} , status=status.HTTP_404_NOT_FOUND)
        
        serializer_discount= serializers.DiscountSerializer(code_check)

        expire_discount = serializer_discount.data ['expiration_date']
        expire_discount =datetime.datetime.strptime (serializer_discount.data ['expiration_date'] , "%Y-%m-%dT%H:%M:%SZ").date()
        now = datetime.datetime.now().date()
        number_of_times = serializer_discount.data['number_of_times']





        # فعلا تعداد دفعات بیشتر از 0  میزاریم بعدش درست میکنیم
                
        if number_of_times > 0 and expire_discount >  now :
            return Response({'message': 'کد تخفیف معتبر است'}, status=status.HTTP_200_OK)
        return Response({'message': 'زمان کد تخفیف منقضی شده است'}, status=status.HTTP_400_BAD_REQUEST)






























