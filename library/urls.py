from django.urls import path,include
from library import views
app_name = 'library'




urlpatterns = [
    path('',views.BookListview.as_view(),name='list'),
    path('add/book/',views.Bookcreateview.as_view(),name='add-book'),
    path('update/book/<int:id>/',views.BookUpdateview.as_view(),name='update-book'),
    path('delete/book/<int:id>/',views.BookDeleteView.as_view(),name='delete-book'),
    path('member/list/',views.MemberListview.as_view(),name='member_list'),
    path('add/member/',views.Membercreateview.as_view(),name='add-member'),
    path('update/member/<int:id>/',views.MemberUpdateview.as_view(),name='update-member'),
    path('delete/member/<int:id>/',views.MemberDeleteView.as_view(),name='delete-member'),
    path('transaction/list/',views.transactionListview.as_view(),name='transaction_list'),
    path('issue_book/<int:member_id>/<int:book_id>/', views.IssueBookView.as_view(), name='issue_book'),
    path('return_book/<int:transaction_id>/', views.ReturnBookView.as_view(), name='return_book'),
]