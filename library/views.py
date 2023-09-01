from datetime import date
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views import generic
from library.models import Book, Member, Transaction
from library.forms import BookForm, MemberForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q


class Baseview(View):
    def get_book_id(self):
        return get_object_or_404(
            Book.objects.all(),
            pk = self.kwargs.get('id')
        )
    def get_member_id(self):
        return get_object_or_404(
            Member.objects.all(),
            pk = self.kwargs.get('id')
        )

class BookListview(View):
    def get(self,request,*args,**kwargs):
        search_name = request.GET.get('search_name')
        book = Book.objects.all()

        if search_name:
            book = book.filter(Q(name__icontains=search_name) | Q(author__icontains=search_name))

        return render(request,'library/book_list.html',{'book':book})


class Bookcreateview(generic.CreateView):
    def get(self, request, *args ,**kwargs):
        return render(
            request,'library/add_book.html',{'form':BookForm()}
        )
    def post(self, request, *args, **kwargs):
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)

            book.save()
            messages.success(
                request,'Book is Successfully created.'
            )
            if request.POST.get('add_more'):
                return redirect('library:add-book')
            return redirect('library:list')
        else:
            return render(
                request,
                'library/add_book.html',{
                    'form':form
                }
            )

class BookUpdateview(Baseview,View):
    def get(self,request,*args,**kwargs):
        book = self.get_book_id()
        form = BookForm(instance=book)
        return render(
            request,'library/update_book.html',{'form':form}
        )
    def post(self,request,*args,**kwargs):
        book = self.get_book_id()
        form = BookForm(request.POST,instance=book)
        if form.is_valid():
            form.save()
            if request.POST.get('add_more'):
                return redirect('library:add-book')
            return redirect('library:list')
        else:
            return render(
                request,'library/update_book.html',{'form':form}
            )


class BookDeleteView(Baseview):
    def delete_record(self,request,*args,**kwargs):
        book = self.get_book_id()
        book.delete()
        return redirect('library:list')
    
    def post(self, request, *args, **kwargs):
        return self.delete_record(request, *args, **kwargs)


class MemberListview(View):
    def get(self,request,*args,**kwargs):
        member = Member.objects.all()

        return render(request,'library/member_list.html',{'member':member})

class Membercreateview(generic.CreateView):
    def get(self, request, *args ,**kwargs):
        return render(
            request,'library/add_member.html',{'form':MemberForm()}
        )
    def post(self, request, *args, **kwargs):
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)

            member.save()
            messages.success(
                request,'Member is Successfully created.'
            )
            if request.POST.get('add_more'):
                return redirect('library:add-member')
            return redirect('library:member_list')
        else:
            return render(
                request,
                'library/add_member.html',{
                    'form':form
                }
            )

class MemberUpdateview(Baseview,View):
    def get(self,request,*args,**kwargs):
        member = self.get_member_id()
        form = MemberForm(instance=member)
        return render(
            request,'library/update_member.html',{'form':form}
        )
    def post(self,request,*args,**kwargs):
        member = self.get_member_id()
        form = MemberForm(request.POST,instance=member)
        if form.is_valid():
            form.save()
            if request.POST.get('add_more'):
                return redirect('library:add-member')
            return redirect('library:member_list')
        else:
            return render(
                request,'library/update_member.html',{'form':form}
            )


class MemberDeleteView(Baseview):
    def delete_record(self,request,*args,**kwargs):
        member = self.get_member_id()
        member.delete()
        return redirect('library:member_list')
    
    def post(self, request, *args, **kwargs):
        return self.delete_record(request, *args, **kwargs)


class transactionListview(View):
    def get(self,request,*args,**kwargs):
        transaction = Transaction.objects.all()

        return render(request,'library/transaction_list.html',{'transaction':transaction})
    



class IssueBookView(View):
    def get(self, request, member_id, book_id):
  
        return render(request, 'library/issue_book.html', {'member_id': member_id, 'book_id': book_id})
    
    def post(self, request, member_id, book_id):
        member = Member.objects.get(pk=member_id)
        book = Book.objects.get(pk=book_id)
        
        if member.outstanding_debt >= 500:
            return redirect('library:member_list', member_id=member_id, error_message='Outstanding debt limit reached.')
        
        if book.quantity > 0:
            transaction = Transaction.objects.create(
                book=book,
                member=member,
                issue_date=date.today(),
                return_date=None
            )
            
            book.quantity -= 1
            book.save()
            
            return redirect('library:member_list', member_id=member_id, success_message='Book issued successfully.')
        else:
            return redirect('library:member_list', member_id=member_id, error_message='Book is not available.')
        


class ReturnBookView(View):
    def post(self, request, transaction_id):
        transaction = Transaction.objects.get(pk=transaction_id)
        
        if transaction.return_date is None:
            days_overdue = (date.today() - transaction.issue_date).days
            if days_overdue > 0:
                transaction.fees = days_overdue * 10  # Assuming Rs. 10 per day fee
        
        book = transaction.book
        book.quantity += 1
        book.save()
        
        member = transaction.member
        member.outstanding_debt += transaction.fees
        member.save()
        
        transaction.return_date = date.today()
        transaction.save()
        
        return redirect('library:member_list', member_id=member.id, success_message='Book returned successfully.')