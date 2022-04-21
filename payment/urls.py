from django.urls import path, include
from rest_framework_nested import routers

from . import views

# эндпоинт для статуса оплаты
from .views import PaymentFromWallet

paymant_router = routers.DefaultRouter()
paymant_router.register('replenishment', views.Replenishment, 'replenishment')
paymant_router.register('payment', views.Payment, 'payment')
paymant_router.register('transaction_history', views.TransactionsHistory, 'transaction_history')

urlpatterns = [
    path('v1/init_payment/', views.InitPayment.as_view(), name='init_payment'),
    path('v1/result_url/', views.ResultUrl.as_view(), name='result_url'),
    path('v1/profile/', include(paymant_router.urls)),
    path('v1/payment_from_wallet/', PaymentFromWallet.as_view(), name='payment_from_wallet')
]

