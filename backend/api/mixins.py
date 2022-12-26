from rest_framework import mixins, viewsets


class PostDeleteViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Миксин для создания или удаления объекта"""


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Миксин для создания и удаления экземпляра"""
