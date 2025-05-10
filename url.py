
from django.urls import path
from . import views
urlpatterns = [

path('servicewise_sys/',views.servicewise_sys,name='servicewise_sys'),
path('ipwise_sys/',views.ipwise_sys,name='ipwise_sys'),
path('portwise_sys/',views.portwise_sys,name='portwise_sys'),
path('servicewise_exp/',views.servicewise_exp,name='servicewise_exp'),
path('ipwise_exp/',views.ipwise_exp,name='ipwise_exp'),
path('portwise_exp/',views.portwise_exp,name='portwise_exp'),
path('ip_wise_top5/',views.ipwiseSorted,name='ipWiseSorted'),
path('ipwise_sys_top5/',views.ipwiseSortedSys,name='ipwiseSortedSys'),
path('ipwise_exp_top5/',views.ipwiseSortedExp,name='ipwiseSortedExp'),
path('servicewise_top5_exp/',views.serviceWiseSortedExp,name='serviceWiseSortedExp'),
path('servicewise_top5_sys/',views.serviceWiseSortedSys,name='serviceWiseSortedSys'),
path('portwise_top5_sys/',views.portWiseSortedSys,name='portWiseSortedSys'),
path('portwise_top5_exp/',views.portWiseSortedExp,name='portWiseSortedExp'),
path('portwise_top5_FiveM/<str:layer>/',views.portWiseTime,name='portWiseSortedFiveM'),
path('ipwise_top5_FiveM/<str:layer>/',views.ipWiseTime,name='ipWiseSortedFiveM'),
path('servicewise_top5_FiveM/<str:layer>/',views.serviceWiseTime,name='serviceWiseSortedFiveM'),
path('newLogin/',views.Login,name="chatBotLogin"),
]
