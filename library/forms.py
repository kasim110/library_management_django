from django import forms

from library.models import Book,Member,Transaction

class BookForm(forms.ModelForm):
    name = forms.CharField(
        label = "Book Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "book_name",
                "placeholder":"Enter Book Name"
            }
        )
    )
    author = forms.CharField(
        label = "Author",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "author",
                "placeholder":"Enter Author"
            }
        )
    )
    quantity = forms.IntegerField(
        label = "Quantity",
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "quantity",
                "placeholder":"Enter Quantity"
            }
        )
    )
    

    class  Meta:
        model = Book
        fields = ['name','author','quantity']



class MemberForm(forms.ModelForm):
    name = forms.CharField(
        label = "Member Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "member_name",
                "placeholder":"Enter Member Name"
            }
        )
    )

    contact = forms.CharField(
        label = "Contact",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "contact",
                "placeholder":"Enter Contact"
            }
        )
    )
    outstanding_debt = forms.DecimalField(
        label = "Outstanding Debt",
        widget=forms.TextInput(
            attrs={
                "class": "form-control formControl",
                "id": "outstanding_debt",
                "placeholder":"Enter Outstanding Debt"
            }
        )
    )
    

    class  Meta:
        model = Member
        fields = ['name','contact','outstanding_debt']