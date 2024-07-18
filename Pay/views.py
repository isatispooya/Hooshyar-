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
from Authentication.models import Auth
from Visit.serializers import KindOfCounselingSerializer
import json

# show invoice before buy
class PayViewset(APIView):
    def get(self, request, kind ):
            Authorization = request.headers.get('Authorization')
            if not Authorization:
                return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = fun.decryptionUser(Authorization)
            user = user.first()
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            code = request.query_params.get('code')
            national_code = user.national_code
            print('farasahm_user')

            rest_api_token = 'ZtqX2dtvjxyYwnjInl8xGhGiynj5uKiO'
            data = {'token' : rest_api_token , 'nc': national_code}
            data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            farasahm_user_asset = requests.post('https://b.fidip.ir/service/assetcustomer',data = data , headers=headers)
            if farasahm_user_asset.status_code == 200:
                try:
                    farasahm_user_asset = farasahm_user_asset.json()
                    off_asset = {'broker':farasahm_user_asset['broker']*0.1}
                    print(off_asset)

                    for i in farasahm_user_asset['asset']:
                        off_asset[i['Symbol']] = int(int(i['VolumeInPrice'])/10000000)/100
                        print(off_asset)
                except ValueError:
                    off_asset = {'broker': 0, 'بتیس1': 0, 'خاتم1': 0, 'ترمه1': 0, 'ویسا1': 0}
                    return Response({'error': 'Failed to parse JSON response from external service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

            kindofcounseling = KindOfCounseling.objects.filter(id=kind).first()
            serializer_kindofcounseling = KindOfCounselingSerializer(kindofcounseling)
            result = {'price' :int (serializer_kindofcounseling.data['price'])}
            off = 0
            try :
                discount = models.Discount.objects.filter(code=code).first()
                print(code)
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

            result ['off'] = off
            result ['off_broker'] = result['price'] * off_asset['broker']
            result ['off_betis'] = result['price'] * off_asset['بتیس1']
            result ['off_khatam'] = result['price'] * off_asset['خاتم1']
            result ['off_terme'] = result['price'] * off_asset['ترمه1']
            result ['off_visa'] = result['price'] * off_asset['ویسا1']
            result ['off_all'] = result ['off'] + result ['off_betis'] + result ['off_khatam'] + result ['off_terme'] + result ['off_visa']
            result ['off_all'] = min(result ['off_all'], result['price'])

            result['final_price'] = result['price'] - result ['off_all']
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



