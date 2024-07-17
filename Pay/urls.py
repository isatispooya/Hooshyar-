from django.urls import path
from .views import PayViewset  , DiscountViewset 

urlpatterns = [
    path('perpay/<int:kind>/', PayViewset.as_view(), name='perpay'),
    path('discount/', DiscountViewset.as_view(), name='discount-code'),

]