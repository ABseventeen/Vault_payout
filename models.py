#Debit status: 1- pending, 2- nach.debit.success, 3-failure, 4 -cancelled, 5-consolidated.settlement.completed, 6-payee credit success
#Should make it only status
class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    digio_transaction_id = models.CharField(max_length=100, default="-")
    created_on = models.DateTimeField(default=timezone.now())
    debit_status = models.IntegerField(default=1)
    failure_reason = models.CharField(max_length=300, default="", null=True, blank=True)

    def __str__(self):
        return str(self.transaction_id)
