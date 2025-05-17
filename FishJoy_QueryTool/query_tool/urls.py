from django.urls import include, path

from .views import Home, FishList, BaitsList, query_tool, delete, AddSpots, add, AddFish, AddBaits, edit, edit_record

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('fish', FishList.as_view(), name='fish'),
    path('baits', BaitsList.as_view(), name='baits'),
    path('query_tool', query_tool, name='query_tool'),
    path('add', add, name='add'),
    path('add_spots', AddSpots.as_view(), name='add_spots'),
    path('add_fish', AddFish.as_view(), name='add_fish'),
    path('add_baits', AddBaits.as_view(), name='add_baits'),
    path('delete', delete, name='delete'),
    path('edit/', edit, name='edit'),
    path('edit_record/<int:id>', edit_record, name='edit_record'),

]
