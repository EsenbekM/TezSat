from django.db.models import Max, Count, OuterRef, Subquery, Q
from django.utils import timezone
from django_q.tasks import async_task
from firebase_admin.messaging import UnregisteredError
from rest_framework import viewsets, mixins, decorators, response, status, exceptions, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from business.permissions import IsBusiness
from category.models import Category
from location.models import Location
from tezsat.mixins import ActionSerializerClassMixin, ActionPermissionsMixin, FilterByRecursion
from tezsat.push_texts import PushText, PushBody
from tezsat.settings import Lang
from . import models, serializers, jobs
from .jobs import create_search_keyword
from .mixins import ListModelStatsMixin, RetrieveModelStatsMixin
from .models import ProductReview, ClaimCategory, Product, ProductPhoto
from .settings import ProductState, PRODUCT_UPVOTE_LIMIT, CurrencyType


class CurrencyView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CurrencySerializer
    authentication_classes = ()
    permission_classes = ()
    pagination_class = None

    def get_queryset(self):
        return models.Rate.objects.all()


class ProductView(FilterByRecursion,
                  ActionSerializerClassMixin,
                  RetrieveModelStatsMixin,
                  ListModelStatsMixin,
                  viewsets.GenericViewSet):
    serializer_class = serializers.ProductSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)
    action_serializer_class = {
        'list': serializers.ShortProductSerializer
    }
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('show_count', 'view_count', 'upvote_date')

    # search_fields = (
    #     'title', 'description', 'location__title_ru', 'location__title_ky', 'category__title_ru', 'category__title_ky'
    # )

    def _filter_price(self, currency, price, option, queryset):
        field = {
            f'price_{currency.lower()}__{option}': price
        }
        return queryset.filter(**field)

    def filter_price(self, queryset):
        currency = self.request.GET.get('currency')
        if not currency or currency not in CurrencyType.all():
            return queryset
        for option in ('lte', 'gte', 'range'):
            field = f'price__{option}'
            price = self.request.GET.get(field)
            if price:
                if option == 'range':
                    price = [int(num) for num in price.split(',')]
                return self._filter_price(currency, price, option, queryset)
        return queryset

    def search_by_query(self, queryset):
        """
        If user makes a search, searching through custom search field in product table or just returning all products
        """
        query_param = self.request.query_params.get('search')
        if query_param:
            async_task(create_search_keyword, query_param)
            queryset = queryset.extra(
                select={
                    "rank": "ts_rank_cd(product.fulltext_field, phraseto_tsquery('russian', %s))"
                },
                select_params=(query_param,),
                where=["product.fulltext_field @@ phraseto_tsquery('russian', %s)"], params=[query_param]
            ).order_by('-rank')

        return queryset

    def filter_location(self, queryset):
        return self.filter_children_ids(queryset, 'location', Location)

    def filter_category(self, queryset):
        return self.filter_children_ids(queryset, 'category', Category)

    def order_price(self, queryset):
        currency = self.request.GET.get('currency')
        if not currency or currency not in CurrencyType.all():
            currency = CurrencyType.KGS
        ordering = self.request.GET.get('ordering')
        if not ordering:
            return queryset
        ordering = ordering.split(',')
        for param in ordering:
            if param == 'price' or param == '-price':
                field = f'{param}_{currency.lower()}'
                return queryset.order_by(field)
        return queryset

    def _filter_parameter_serialize(self, title, params):
        params = params.split(',')
        data = []
        errors = []
        for param in params:
            try:
                data.append(int(param))
            except Exception:
                errors.append('A valid integer required')
        if errors:
            raise exceptions.ValidationError({title: errors})
        return data

    def filter_parameter(self, queryset):
        options = self.request.GET.get('options')
        if not options:
            return queryset
        options = self._filter_parameter_serialize('options', options)
        # '''select p.id,
        #   p.title,
        #   count(pp.product_id) as c
        # from product as p
        # inner join product_parameter as pp on p.id = pp.product_id
        # where pp.option_id in (7, 2)
        # group by pp.product_id
        # having count(pp.product_id) = 2
        # order by c desc
        # '''
        queryset = queryset \
            .filter(parameters__option_id__in=options) \
            .annotate(option_count=Count('parameters__product_id')) \
            .filter(option_count=len(options))
        return queryset

    def filter_user(self, queryset):
        user_id = self.request.GET.get('user')
        if not user_id:
            if not self.detail:
                return queryset.filter(state=ProductState.ACTIVE)
            return queryset.filter(state__in=[ProductState.ACTIVE, ProductState.INACTIVE])
        try:
            user_id = int(user_id)
        except Exception:
            raise exceptions.ValidationError({'user': 'field must be pure integer'})
        queryset = queryset.filter(user_id=user_id, state__in=[ProductState.ACTIVE, ProductState.INACTIVE])
        return queryset

    def exclude_product(self, queryset):
        product = self.request.query_params.get("product")
        if not product:
            return queryset
        return queryset.exclude(id=product)

    def filter_business(self, queryset):
        is_business = self.request.GET.get('is_business')
        if is_business is None:
            return queryset
        is_business = is_business.lower()
        if is_business == 'true':
            qs = queryset.filter(user__business__is_active=True)

        elif is_business == 'false':
            qs = queryset.filter(Q(user__business__isnull=True) | Q(user__business__is_active=False))
        else:
            raise exceptions.ValidationError({'is_business': 'true/false only acceptable'})
        return qs

    def reorder_products(self, queryset):
        if self.request.GET.get('is_business'):
            return queryset
        business_products = queryset.filter(user__business__is_active=True)
        regular_products = queryset.filter(Q(user__business__isnull=True) | Q(user__business__is_active=False))
        result = []
        len_regular = len(regular_products)
        len_business = len(business_products)
        if len_regular < len_business:
            max_index = len_regular
            max_queryset = business_products
        else:
            max_index = len_business
            max_queryset = regular_products
        for i in range(max_index):
            result += [business_products[i], regular_products[i]]
        result += max_queryset[max_index:]
        return result

    def filter_similar(self, queryset):
        id = self.request.query_params.get('similar_category', None)
        if id and len(queryset) < 28:
            instance = Category.objects.get(id=id).parent
            queryset = queryset.values_list('id', flat=True)
            products = Product.objects.filter(category=instance)
            queryset = queryset.union(products)
            queryset = Product.objects.filter(id__in=queryset)
            photo_qs = ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
            queryset = queryset.annotate(photo=Subquery(photo_qs[:1]))
        return queryset

    def filter_queryset(self, queryset):
        queryset = self.filter_user(queryset)
        queryset = self.filter_category(queryset)
        queryset = self.filter_parameter(queryset)
        queryset = self.filter_location(queryset)
        queryset = self.filter_price(queryset)
        queryset = self.exclude_product(queryset)
        queryset = self.filter_similar(queryset)
        # todo: uncomment
        queryset = self.filter_business(queryset)
        queryset = queryset.order_by('-upvote_date')
        queryset = self.order_price(queryset)
        queryset = super().filter_queryset(queryset)
        queryset = self.search_by_query(queryset)
        return queryset

    def get_queryset(self):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        qs = models.Product.objects.select_related('user', 'user__business').prefetch_related('favorites', 'likes'). \
            annotate(photo=Subquery(photo_qs[:1]))
        return qs.all()

    @decorators.action(['GET'], detail=False)
    def max_price(self, request):
        currency = self.request.GET.get('currency')
        if not currency or currency not in CurrencyType.all():
            raise exceptions.ValidationError('invalid currency')
        queryset = self.get_queryset()
        field = f'price_{currency.lower()}'
        aggregated = queryset.aggregate(Max(field))
        if not aggregated:
            price = 0
        else:
            price = aggregated[f'{field}__max']
        return response.Response(data={
            "price": price
        })

    @decorators.action(['POST'], detail=True, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def claim(self, request, pk):
        product = self.get_object()
        data = dict()
        data['user'] = request.user.id
        data['product'] = product.id
        serializer = serializers.ClaimSerializer(data={**request.data, **data}, context={'request': request})
        serializer.is_valid(True)
        serializer.save()
        return response.Response(data=serializer.data)

    @decorators.action(['POST'], detail=True, authentication_classes=(),
                       permission_classes=())
    def call(self, request, pk):
        product = self.get_object()
        jobs.update_call_count(product)
        # async_task(jobs.update_call_count, product, task_name='update call count')
        return response.Response(status=status.HTTP_204_NO_CONTENT)

class ProductClaimView(ActionSerializerClassMixin, mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ClaimCategorySerializer

    def get_queryset(self):
        return ClaimCategory.objects.filter(language=self.request.user.language)


class PersonalProductView(ActionSerializerClassMixin, viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    action_serializer_class = {
        'list': serializers.ShortProductSerializer,
        # 'partial_update': serializers.ChangeProductStateSerializer,
        # 'update': serializers.ChangeProductStateSerializer
    }

    # def filter_queryset(self, queryset):
    #     return queryset.exclude(state=ProductState.DELETED). \
    #         exclude(state=ProductState.BLOCKED).order_by('-upvote_date').all()
    filterset_fields = ('state',)

    def get_queryset(self):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        return models.Product.objects.select_related('user', 'location').prefetch_related('favorites', 'likes'). \
            filter(user=self.request.user,
                   state__in=[ProductState.ACTIVE, ProductState.ON_REVIEW, ProductState.INACTIVE]). \
            annotate(photo=Subquery(photo_qs[:1])).order_by('-creation_date')

    def perform_destroy(self, instance):
        instance.state = ProductState.DELETED
        instance.save()

    @decorators.action(['POST'], detail=True, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def upvote(self, request, pk):
        product = self.get_object()
        now = timezone.now()
        time_passed = now - product.upvote_date
        if time_passed >= PRODUCT_UPVOTE_LIMIT:
            product.upvote_date = now
            product.save()
            return response.Response(status=status.HTTP_200_OK)
        else:
            wait = PRODUCT_UPVOTE_LIMIT - time_passed
            raise exceptions.ValidationError(f'you can upvote in {wait}')

    @decorators.action(['GET'], detail=True, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsBusiness,))
    def stats(self, request, pk):
        if hasattr(request.user, 'business') and request.user.business.is_active:
            product = models.Product.objects.prefetch_related('favorites', 'likes', 'reviews').filter(pk=pk,
                                                                                                      user=request.user).first()
            if not product:
                raise exceptions.NotFound('product not found')
            return response.Response(data=serializers.ProductStatisticSerializer(instance=product).data)
        else:
            raise exceptions.PermissionDenied()


class PhotoUploadView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PhotoUploadSerializer


class FavoriteView(ActionSerializerClassMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    action_serializer_class = {
        "list": serializers.ShortProductSerializer,
        "create": serializers.FavoriteCreationSerializer
    }

    def perform_destroy(self, instance):
        self.request.user.favorites.remove(instance)

    def get_queryset(self):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('photo')
        return self.request.user.favorites.filter(state__in=(ProductState.ACTIVE, ProductState.INACTIVE)). \
            annotate(favorite_count=Count('favorites'), photo=Subquery(photo_qs[:1]))

    @decorators.action(['POST'], detail=False, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def clear(self, request):
        self.request.user.favorites.clear()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(ActionSerializerClassMixin,
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    action_serializer_class = {
        "list": serializers.ShortProductSerializer,
        "create": serializers.LikeCreationSerializer
    }

    def perform_destroy(self, instance):
        self.request.user.likes.remove(instance)

    def get_queryset(self):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('photo')
        return self.request.user.likes.filter(state__in=(ProductState.ACTIVE, ProductState.INACTIVE)). \
            annotate(favorite_count=Count('favorites'), photo=Subquery(photo_qs[:1]))

    @decorators.action(['POST'], detail=False, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def clear(self, request):
        self.request.user.likes.clear()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewView(ActionSerializerClassMixin,
                        ActionPermissionsMixin,
                        viewsets.ModelViewSet):
    serializer_class = serializers.ProductReviewSerializer

    action_permissions = {
        'list': (AllowAny,),
        'retrieve': (AllowAny,)
    }

    def get_parent(self):
        parent = models.Product.objects.prefetch_related('reviews').select_related('user') \
            .filter(pk=self.kwargs['product_pk']).first()
        if not parent:
            raise exceptions.NotFound(f'product with given id {self.kwargs["product_pk"]} not found')
        return parent

    def check_existence(self, user, product):
        if models.ProductReview.objects.filter(user=user, product=product).exists():
            raise exceptions.ValidationError('you can write review only once for product')

    def perform_create(self, serializer):
        product = self.get_parent()
        product_user = product.user
        if hasattr(product_user, 'business') and product_user.business.is_active and not product.rating_disabled:
            self.check_existence(self.request.user, product)
            serializer.save(user=self.request.user, product=product)
            title = PushText.new_review[product_user.language]
            body = PushBody.new_review[product_user.language]
            try:
                product_user.send_message(title=title, body=body, data={'product_id': str(product.id)})
            except UnregisteredError:
                pass
            return response.Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.ValidationError('product not allowed to be reviewed', 'not_allowed')

    def get_queryset(self):
        self.get_parent()
        if self.action in ('list', 'retrieve'):
            return models.ProductReview.objects.filter(product_id=self.kwargs['product_pk'])
        else:
            return models.ProductReview.objects.filter(product_id=self.kwargs['product_pk'], user=self.request.user)

    @decorators.action(['POST', 'DELETE'], detail=True, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def response(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = serializers.ProductReviewResponseSerializer(data=request.data)
            serializer.is_valid(True)
            product = self.get_parent()
            if request.user.id != product.user.id:
                raise exceptions.PermissionDenied()
            review = product.reviews.filter(pk=self.kwargs['pk']).first()
            if not review:
                raise exceptions.NotFound()
            review.response = serializer.validated_data['response']
            review.response_date = timezone.now()
            review.save()
            title = PushText.response_review[product.user.language]
            body = PushBody.response_review[product.user.language]
            review = get_object_or_404(ProductReview, pk=kwargs['pk'])
            review.user.send_message(title=title, body=body, data={'product_id': f"{product.id}"})
            return response.Response(
                data=serializers.ProductReviewSerializer(instance=review, context={'request': request}).data)
        else:
            review = get_object_or_404(ProductReview, pk=self.kwargs['pk'])
            review.response = None
            review.save()
            return response.Response(status=status.HTTP_200_OK)

    @decorators.action(['POST'], detail=True, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def claim(self, request, *args, **kwargs):
        serializer = serializers.ProductReviewClaimSerializer(data=request.data)
        serializer.is_valid(True)
        product = self.get_parent()
        if request.user.id != product.user.id:
            raise exceptions.PermissionDenied()
        review = product.reviews.filter(pk=self.kwargs['pk']).first()
        if not review:
            raise exceptions.NotFound()
        review.claim = serializer.validated_data['message']
        review.claim_date = timezone.now()
        review.save()
        return response.Response(
            data=serializers.ProductReviewSerializer(instance=review, context={"request": request}).data)
