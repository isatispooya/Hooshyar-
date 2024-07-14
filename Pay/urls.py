from django.urls import path
from .views import PayViewset  , DiscountViewset ,invoice

urlpatterns = [
    path('perpay/<int:kind>/', PayViewset.as_view(), name='perpay'),
    path('discount/', DiscountViewset.as_view(), name='discount-code'),
    path('invoice/', invoice.as_view(), name='invoice'),

]