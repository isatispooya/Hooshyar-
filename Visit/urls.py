from django.urls import path
from .views import  VisitViewset  , KindOfCounselingViewset ,VisitConsultationsViewset ,VisitConsultationsDetialViewset ,CardBoxUserViewSet ,CardBoxConsultantViewset
urlpatterns = [
    path('visit/',VisitViewset.as_view(), name='visit'),
    path('cardbox/user/',CardBoxUserViewSet.as_view(), name='card-box-user'),
    path('cardbox/consultant/',CardBoxConsultantViewset.as_view(), name='card-box-consultant'),
    path('kindofcounseling/',KindOfCounselingViewset.as_view(), name='kindofcounseling'),
    path('visit/consultations/list/',VisitConsultationsViewset.as_view(), name='visit-consultations-list'),
    path('visit/consultations/<int:id>/',VisitConsultationsDetialViewset.as_view(), name='visit-consultations-detail'),

]


