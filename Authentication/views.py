from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , generics
from GuardPyCaptcha.Captch import GuardPyCaptcha
from . import models
from . import serializers
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from . import fun
import random


frm ='30001526'
usrnm = 'isatispooya'
psswrd ='5246043adeleh'

def SendSms(snd,txt):
    txt = f'کد تایید :{txt}'
    resp = requests.get(url=f'http://tsms.ir/url/tsmshttp.php?from={frm}&to={snd}&username={usrnm}&password={psswrd}&message={txt}').json()
    print(txt)
    return resp


# captcha
class CaptchaViewset (APIView) :
    def get (self , request) :
        captcha = GuardPyCaptcha()
        captcha = captcha.Captcha_generation (num_char = 4 , only_num = True) 
        return Response (captcha , status = status.HTTP_200_OK)
    
# Otp as User
class OtpViewset  (APIView) :
    def post (self , request) : 
        captcha = GuardPyCaptcha ()

        captcha = captcha.check_response (request.data ['encrypted_response'],request.data ['captcha'] )
        if False :
            result = {'message' : 'کد کپچا صحیح نیست'}
            return Response (result , status= status.HTTP_406_NOT_ACCEPTABLE)
        mobile = request.data ['mobile']
        if not mobile:
            return Response({'message': 'شماره همراه لازم است'}, status=status.HTTP_400_BAD_REQUEST)
        try :
            user = models.Auth.objects.get(mobile = mobile)
            result = {'registered' : True , 'message' : 'کد تایید ارسال شد'}    

        except models.Auth.DoesNotExist: 
            result = {'registered' : False , 'message' : 'کد تایید ارسال شد'}    

        code = 11111 #random.randint(10000,99999)
        otp = models.Otp(mobile=mobile,code =code)
        otp.save()
        SendSms(mobile ,code)

        return Response(result,status=status.HTTP_200_OK)

# Login as user 
class LoginViewset (APIView) :
    def post (self,request) :
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        if not mobile or not code:
            return Response({'message': 'شماره همراه و کد تأیید الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = models.Auth.objects.get(mobile=mobile)
        except:
            result = {'message': ' شماره موبایل موجود نیست لطفا ثبت نام کنید'}
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        try:
            otp_obj = models.Otp.objects.filter(mobile=mobile , code = code ).order_by('-date').first()
        except :
            
            return Response({'message': 'کد تأیید نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp = serializers.OtpSerializer(otp_obj).data
        if otp['code']== None :
            result = {'message': 'کد تأیید نامعتبر است'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
        otp = serializers.OtpSerializer(otp_obj).data
        dt = datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(otp['date'].replace("Z", "+00:00"))
        
        dt = dt.total_seconds()

        if dt >120 :
            result = {'message': 'کد معتبر نیست'}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = models.Auth.objects.get(mobile=mobile)
        except models.Auth.DoesNotExist:
            return Response({'message': 'کاربری با این شماره همراه وجود ندارد'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        otp_obj.delete()
        token = fun.encryptionUser(user)

        print(user)
        return Response({

            'access': token,
        }, status=status.HTTP_200_OK)
    



# Otp as Consultant
class OtpConsultant (APIView) :
    def post (self, request) :
        captcha = GuardPyCaptcha()
        captcha = captcha.check_response(request.data['encrypted_response'] , request.data ['captcha'])
        if False :
            return Response({'message' : 'کد کپچا صحیح نیست'} , status=status.HTTP_406_NOT_ACCEPTABLE)
        mobile = request.data ['mobile']
        if not mobile :
            return Response({'message' : 'شماره همراه مشاور لازم است'})
        try :
            consultant = models.Consultant.objects.get(phone = mobile)
            result = {'registered' : True , 'message' : 'کد تایید ارسال شد'}
        except models.Consultant.DoesNotExist:
            result = {'registered' : False , 'message' : 'مشاور با این شماره همراه وجود ندارد'}

        code = 11111 #random.randint(10000,99999)
        otp = models.Otp(mobile = mobile , code = code)
        otp.save()
        SendSms(mobile ,code)
        return Response (result , status=status.HTTP_200_OK)

        
    

# Login as Consultant 
class LoginConsultant (APIView) :
    def post (self,request) :
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        
        if not mobile or not code :
            return Response ({'message' : 'کد تایید و شماره همراه الزامی است '} , status=status.HTTP_406_NOT_ACCEPTABLE)
        try :
            consultant = models.Consultant.objects.get(phone = mobile)
        except :
            result = {'message' : 'مشاور با این شماره همراه ثبت نام نشده است لطفا ثبت نام کنید'}
            return Response (result , status=status.HTTP_404_NOT_FOUND)
        try :
            code_otp = models.Otp.objects.filter(code=code , mobile=mobile).order_by('-date').first()
        except:
            return Response ({'message' : ' 1 کد تایید نامعتبر است'},status=status.HTTP_400_BAD_REQUEST)
        
        otp = serializers.OtpSerializer(code_otp).data
        if otp ['code'] == None :
            return Response ({'message' : ' 2 کد تایید نامعتبر است'} , status=status.HTTP_400_BAD_REQUEST)
        now = datetime.datetime.now(datetime.timezone.utc)
        otp_date = datetime.datetime.fromisoformat(otp['date'].replace("Z", "+00:00"))
        dt = now-otp_date
        dt = dt.total_seconds()
        if dt >120 :
            return Response ({'message' : 'زمان کد به پایان رسیده است'})
        try :
            consultant = models.Consultant.objects.get(phone = mobile)
        except :
            return Response ({'message' : 'کاربری با این شماره همراه وجود ندارد'} , status=status.HTTP_404_NOT_FOUND)
        code_otp.delete()

        token = fun.encryptionConsultant(consultant)
        
        return Response ({'access' : token} , status=status.HTTP_200_OK)


# Sign up as user
class AuthCreateView(generics.CreateAPIView):
    queryset = models.Auth.objects.all()
    serializer_class = serializers.AuthSerializer

    def post(self, request):
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        user = models.Auth.objects.filter(mobile=mobile ).first()
        otp_code = models.Otp.objects.filter(mobile=mobile).first()
        if str(code) != str(code) :
            return Response({'message': 'کد نادرست است'}, status=status.HTTP_400_BAD_REQUEST)
        if user :
            return Response({'message': 'شماره موبایل موجود است'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            result = (serializer.data)
        user = models.Auth.objects.filter(mobile=mobile).first()
        token = fun.encryptionUser(user)

        return Response({'access': token , 'user' : result}, status=status.HTTP_200_OK)
        




# all Consultant profile for user
class ConsultantViewset(APIView) :
    def get (self , request) :
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        consultant = models.Consultant.objects.all()
        if not consultant.exists():
            return Response([], status=status.HTTP_200_OK)
        
        serializer = serializers.ConsultantSerializer(consultant, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)



# show consultant profile for consultant
class ConsultantProfileViewset (APIView) :
    def get (self,request) :
        Authorization = request.headers['Authorization']
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        consultant = fun.decryptionConsultant(Authorization)
        if not consultant:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        consultant_instance = consultant.first()
        serializer_consultant = serializers.ConsultantSerializer(consultant_instance).data
        return Response (serializer_consultant , status=status.HTTP_200_OK)




   


# User Profile 
class UserProfileViewset(APIView):
    # show user profile
    def get(self , request):
        Authorization = request.headers['Authorization']
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user_instance = user.first()
        serializer = UserSerializer(user_instance)
        return Response(serializer.data,status=status.HTTP_200_OK)

    # update user profile
    def put (self,request) :
        Authorization = request.headers['Authorization']
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user_instance = user.first()

        serializer = UserSerializer(user_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







# Agreement update false  to  true
class AgreementViewset(APIView):
    def put(self, request):
        Authorization = request.headers.get('Authorization')
        if not Authorization:
            return Response({'error': 'Authorization header is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = fun.decryptionUser(Authorization)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user_instance = user.first()
        user_instance.agreement = True
        user_instance.save()  

        return Response({'message': 'update'}, status=status.HTTP_200_OK)