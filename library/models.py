from django.db import models
from django_extensions.db.models import TimeStampedModel



class Book(TimeStampedModel):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    isbn = models.CharField(max_length=20,null=True ,blank=True)
    publisher = models.CharField(max_length=255,null=True,blank=True)
    page = models.PositiveIntegerField(null=True,blank=True)



    def __str__(self):
        return self.name

class Member(TimeStampedModel):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    outstanding_debt = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Transaction(TimeStampedModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,related_name='transaction_book')
    member = models.ForeignKey(Member, on_delete=models.CASCADE,related_name='transaction_member')
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0)


    def __str__(self):
        return f"{self.book}"
