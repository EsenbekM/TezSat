import datetime
from datetime import datetime as dt
from datetime import time
from django.db.models import OuterRef, Subquery, F
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, mixins, filters, response, status, generics, decorators
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from category.models import Category
from product.models import ProductPhoto, ProductReview, Product
from product.serializers import ShortProductWithStatsSerializer, ProductReviewSerializer
from tezsat.mixins import ActionSerializerClassMixin, ActionPermissionsMixin, FilterByRecursion
from users.authentication import JWTSessionAuthentication
from users.settings import RequestStatuses
from . import serializers, models, services
from .models import BusinessCatalog, AddModal
from .permissions import IsBusiness, IsBusinessManyOwner, IsBusinessOrReadOnly, IsBusinessOrAdmin
from .serializers import ProductSerializerPhoto


class BusinessViewSet(FilterByRecursion,
                      ActionSerializerClassMixin,
                      ActionPermissionsMixin,
                      viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.BusinessSerializer
    action_serializer_class = {
        'list': serializers.ShortBusinessSerializer
    }
    action_permissions = {
        'list': (permissions.AllowAny,),
        'retrieve': (permissions.AllowAny,)
    }

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ('rating', 'creation_date')
    search_fields = ('name', 'description')

    def filter_category(self, queryset):
        return self.filter_children_ids(queryset, 'category', Category)

    def filter_queryset(self, queryset):
        queryset = self.filter_category(queryset)
        queryset = super().filter_queryset(queryset)
        return queryset

    def get_queryset(self):
        return models.Business.objects.filter(is_active=True).all()


class BusinessRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.BusinessRequestSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BusinessApiView(generics.GenericAPIView):
    serializer_class = serializers.BusinessSerializer
    permission_classes = (IsBusiness,)
    pagination_class = None

    @swagger_auto_schema(responses={'200': serializers.BusinessSerializer()}, tags=['business'])
    def get(self, request):
        business = request.user.business
        serializer = self.serializer_class(instance=business, context={'request': request})
        user = request.user
        if user.request_status == RequestStatuses.ACCEPTED:
            user.request_status = RequestStatuses.SUCCESS
            user.save()
        return response.Response(data=serializer.data)

    def patch(self, request):
        serializer = self.serializer_class(request.user.business, data=request.data, partial=True,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data=serializer.data)


class BusinessStatsApiView(generics.GenericAPIView):
    serializer_class = serializers.BusinessStatsSerializer
    permission_classes = (IsBusinessOrAdmin,)
    pagination_class = None
    authentication_classes = (JWTSessionAuthentication, SessionAuthentication)

    def get(self, request):
        start_date, end_date = request.query_params.get('start', ""), request.query_params.get('end', "")
        statistics = services.business_stats(None, start_date=start_date, end_date=end_date, user_id=request.user.id)
        return response.Response(data=statistics)


class BusinessAdminStatsApiView(generics.GenericAPIView):
    serializer_class = serializers.BusinessStatsSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = None
    authentication_classes = (SessionAuthentication,)
    lookup_url_kwarg = 'pk'

    def get(self, request, *args, **kwargs):
        start_date, end_date = request.query_params.get('start', ""), request.query_params.get('end', "")
        statistics = services.business_admin_statistics(start_date=start_date, end_date=end_date,
                                                        business_id=kwargs['pk'])
        return response.Response(data=statistics)


class BusinessProductsStatApiView(generics.GenericAPIView):
    serializer_class = ShortProductWithStatsSerializer
    permission_classes = (IsBusiness,)

    # TODO: Added proper validation and serialization
    def get(self, request, *args, **kwargs):
        start_date, end_date = request.query_params.get('start', ""), request.query_params.get('end', "")
        statistics = services.business_stats(kwargs['pk'], start_date=start_date, end_date=end_date)
        return response.Response(data=statistics, status=status.HTTP_200_OK)


class DeactivateBusinessView(generics.GenericAPIView):
    permission_classes = (IsBusiness,)
    serializer_class = serializers.BusinessDeactivateSerializer

    @swagger_auto_schema(responses={'204': ''}, tags=['business'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        business = request.user.business
        business.is_active = False
        business.deactivation_message = serializer.validated_data['message']
        business.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class BusinessBranchesView(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    View only for the purpose of adding, deleting, and updating branches of business
    """
    serializer_class = serializers.BusinessBranchSerializer
    permission_classes = (IsBusiness, IsBusinessManyOwner)

    def get_queryset(self):
        return models.BusinessBranch.objects.filter(business=self.request.user.business)

    def create(self, request, *args, **kwargs):
        services.create_business_extra(request.data, request.user.business, models.BusinessBranch)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessContactsView(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    View only for the purpose of adding, deleting, and updating contacts of business
    """
    serializer_class = serializers.BusinessContactSerializer
    permission_classes = (IsBusiness, IsBusinessManyOwner)

    def create(self, request, *args, **kwargs):
        services.create_business_extra(request.data, request.user.business, models.BusinessContact)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return models.BusinessContact.objects.filter(business=self.request.user.business)


class BusinessScheduleView(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    View only for the purpose of adding, deleting, and updating schedule of business
    """
    serializer_class = serializers.BusinessScheduleSerializer
    permission_classes = (IsBusiness, IsBusinessManyOwner)

    def get_queryset(self):
        return models.BusinessSchedule.objects.filter(business=self.request.user.business)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        services.create_schedules(serializer.data, request.user.business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessBannersView(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    View only for the purpose of adding, deleting, and updating banners of business
    """
    serializer_class = serializers.BusinessBannerSerializer
    permission_classes = (IsBusiness, IsBusinessManyOwner)

    def get_queryset(self):
        return models.BusinessBanner.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)


class BusinessCatalogView(mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    View only for the purpose of adding, deleting, and updating banners of business
    """
    permission_classes = (IsBusinessOrReadOnly,)
    pagination_class = None
    lookup_url_kwarg = 'catalog_id'

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.BusinessCatalogCreateSerializer
        else:
            return serializers.BusinessCatalogSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, limit=4)
        return Response(serializer.data)

    def get_queryset(self):
        pk = self.kwargs['pk']
        return models.BusinessCatalog.objects. \
            filter(business_id=pk).prefetch_related('products')

    def retrieve(self, request, *args, **kwargs):
        catalog = get_object_or_404(self.get_queryset(), pk=kwargs['catalog_id'])
        serializer = self.get_serializer(catalog)
        return response.Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

    def perform_update(self, serializer):
        products = self.request.data.get('products', None)
        serializer.save(business=self.request.user.business, products=products)

    # TODO destroy products in catalogs
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        products = request.data.get("products")
        if products:
            [BusinessCatalog.objects.get(id=kwargs['catalog_id']).products.remove(i)
             for i in Product.objects.filter(id__in=products)]
        else:
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessDiscountView(mixins.ListModelMixin, mixins.CreateModelMixin, ActionPermissionsMixin,
                           viewsets.GenericViewSet, ):
    pagination_class = None
    serializer_class = serializers.ShortProductSerializer
    action_permissions = {
        'list': (AllowAny,),
        'create': (IsBusiness, IsBusinessManyOwner)
    }

    def get_queryset(self):
        business_id = self.kwargs['pk']
        photo_qs = ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        qs = models.Product.objects.select_related('user', 'user__business').prefetch_related('favorites', 'likes'). \
            annotate(photo=Subquery(photo_qs[:1]))
        return qs.filter(discount_price_kgs__isnull=False,
                         discount_price_usd__isnull=False, user__business__id=business_id)

    def create(self, request, *args, **kwargs):
        products, discount = request.data['products'], request.data['discount']
        if discount == 0:
            models.Product.objects.filter(id__in=products).update(discount_price_kgs=None, discount_price_usd=None)
            return response.Response(data={"message": "discount applied"}, status=status.HTTP_200_OK)
        models.Product.objects.filter(id__in=products). \
            update(discount_price_kgs=F('price_kgs') * ((100 - discount) / 100),
                   discount_price_usd=F('price_usd') * ((100 - discount) / 100))
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.action(['GET'], detail=False, authentication_classes=(), permission_classes=(),
                       url_path='last')
    def last_discounts(self, request, *args, **kwargs):
        business_id = self.kwargs['pk']
        discounts = models.Product.objects.filter(discount_price_kgs__isnull=False,
                                                  discount_price_usd__isnull=False,
                                                  user__business__id=business_id).order_by('-id')[:4]
        serializer = ProductSerializerPhoto(discounts, many=True, context={"request": request}).data
        return response.Response(data=serializer, status=status.HTTP_200_OK)


class ReviewsView(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductReviewSerializer
    pagination_class = None
    permission_classes = (IsBusiness, IsBusinessManyOwner)

    def list(self, request, *args, **kwargs):
        reviews = ProductReview.objects.filter(product__user_id=request.user, is_read=False)
        serializer = self.get_serializer(reviews, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = ProductReview.objects.filter(product__user_id=request.user, is_read=False)
        instance.update(is_read=True)
        return response.Response(status=status.HTTP_200_OK)

class EveryThreeDays(generics.GenericAPIView):
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = None

    def get(self, request, *args, **kwargs):
        formats = '%Y-%m-%d %H:%M:%S'
        model = AddModal.objects.first()
        data = {'status': False}
        date = datetime.datetime.strptime(model.date.strftime(formats), formats)
        times = [time(hour=12), time(hour=14), time(hour=17), time(hour=19)] # показ по периоду
        if dt.now().date() == date.date():
            if (dt.now().time() >= times[0] and dt.now().time() <= times[1]):
                data['status'] = True
            elif (dt.now().time() >= times[-2] and dt.now().time() <= times[-1]):
                data['status'] = True
                model.date = dt.now() + datetime.timedelta(days=3)
                model.save()
        return response.Response(data=data)
