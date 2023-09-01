from datetime import date
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views import generic
from library.models import Book, Member, Transaction
from library.forms import BookForm, FrappeImportForm, IssueBookForm, MemberForm, ReturnBookForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
import requests


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
    def get(self, request):
        form = IssueBookForm()
        return render(request, 'library/issue_book.html', {'form': form})
  
    def post(self, request):
        form = IssueBookForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            book = form.cleaned_data['book']
            quantity = form.cleaned_data['quantity']

            if member.outstanding_debt > 500:
                return render(request, 'library/error.html', {'message': 'Member has outstanding debt exceeding ₹500. Cannot issue book.'})

            # Create transaction records for the selected member and book
            for _ in range(quantity):
                transaction = Transaction(member=member, book=book,issue_date=date.today())
                transaction.save()

            # Update the book's quantity in stock
            book.quantity -= quantity
            book.save()

            return redirect('library:transaction_list')
        


class ReturnBookView(View):
    def get(self, request):
        form = ReturnBookForm()
        return render(request, 'library/return_book.html', {'form': form})

    def post(self, request):
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            book = form.cleaned_data['book']
            quantity = form.cleaned_data['quantity']


            if member.outstanding_debt > 500:
                return render(request, 'library/error.html', {'message': 'Member has outstanding debt exceeding ₹500. Cannot issue book.'})

            # Check if there are existing transaction records to modify
            existing_transactions = Transaction.objects.filter(
                member=member, book=book, return_date__isnull=True
            ).order_by('issue_date')[:quantity]

            for transaction in existing_transactions:
                # Calculate fees for overdue books
                days_overdue = (date.today() - transaction.issue_date).days
                if days_overdue > 0:
                    transaction.fees = days_overdue * 10  # Assuming Rs. 10 per day fee


                transaction.return_date = date.today()
                transaction.save()

            book.quantity += quantity
            book.save()

            member.outstanding_debt += transaction.fees
            member.save()

            

            return redirect('library:transaction_list')
        return render(request, 'library/return_book.html', {'form': form})
    



def import_books_from_frappe(request):
    if request.method == 'POST':
        form = FrappeImportForm(request.POST)
        if form.is_valid():
            # Get form data
            title = form.cleaned_data['title']
            authors = form.cleaned_data['authors']
            isbn = form.cleaned_data['isbn']
            publisher = form.cleaned_data['publisher']
            page = form.cleaned_data['page']
            quantity = form.cleaned_data['quantity']

            # Build the API URL with parameters
            api_url = 'https://frappe.io/api/method/frappe-library'
            params = {
                'title': title,
                'authors': authors,
                'isbn': isbn,
                'publisher': publisher,
                'page': page,
                'limit_start': 0,
                'limit_page_length': quantity,
            }

            # Make a GET request to the Frappe API
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                # Process the API response here and create book records
                # For example, you can parse the JSON response and create Book objects

                return redirect('library:list')  # Redirect to success page
            else:
                return render(request, 'error.html', {'message': 'Failed to import books'})  # Show an error message

    else:
        form = FrappeImportForm()

    return render(request, 'library/import_book.html', {'form': form})