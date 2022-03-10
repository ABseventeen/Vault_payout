@csrf_exempt
@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def nach_debit_status(request): 
    data = JSONParser().parse(request)
    try:
        if 'event' in data and 'payload' in data and 'nach_debit' in data["payload"]:
            transaction = Transaction.objects.get(digio_transaction_id=data["payload"]["nach_debit"]["transaction_id"])
            if data["event"] == "nach.debit.success":
                transaction.debit_status = 2
                # no payout here
            if data["event"] == "nach.debit.failed":
                transaction.debit_status = 3 
                transaction.failure_reason = data["payload"]["nach_debit"]["failure_description"]
                transaction.save()
            return JsonResponse(data={"message": "Transaction details updated"}, status=200)
        else:
            return JsonResponse(data={"message": "Not in proper format"}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse(data={"message": "Transaction not found"}, status=200)

@csrf_exempt
@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def settlement_status(request):
    data = JSONParser().parse(request)
    try:
        if 'event' in data and 'payload' in data and 'consolidated_settlement' in data["payload"]:
            transaction = Transaction.objects.get(digio_transaction_id=data["payload"]["consolidated_settlement"]["transaction_id"])
            if data["event"] == "consolidated.settlement.completed":
                transaction.debit_status = 5
                # Initiate payout from Hypto
                initiate_payout(request) # Should we pay here instatly or wait for some time?
                transaction.save()
            return JsonResponse(data={"message": "Transaction amount received in our account"}, status=200)
        else:
            return JsonResponse(data={"message": "Not in proper format"}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse(data={"message": "Transaction not found"}, status=200)

@csrf_exempt
@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def payee_credit_status(request):
    data = JSONParser().parse(request)
    try:
        if 'payload' in data:
            transaction = Transaction.objects.get(digio_transaction_id=data["reference_number"])
            if data['status'] == "COMPLETED":
                transaction.debit_status = 6
                transaction.save()
            return JsonResponse(data={"message": "Transaction made to payee"}, status=200)
        else:
            return JsonResponse(data={"message": "Not in proper format"}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse(data={"message": "Transaction not found"}, status=200)      

    
@csrf_exempt
@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.Allowany])
def initiate_payout(request):
    try:
        data = JSONParser().parse(request)
        transaction = Transaction.objects.get(transaction_id=data["transaction_id")
        payment = Payment.objects.get(id=transaction.payment)
        receiving_account = BankAccount.objects.get(id=payment.receiving_account)
        d = datetime.datetime.now() + datetime.timedelta(days=1)
        payload = {
                {
                "amount": payment.amount,
                "payment_type": "NEFT",
                "ifsc": receiving_account.ifsc,
                "number": receiving_account.account_no,
                "note": "Fund Transfer",
                # "udf1": "UDF Test 1",
                # "udf2": "UDF Test 2",
                # "udf3": "UDF Test 3",
                "reference_number": "transaction.digio_transaction_id", #is this schedule id or txn id (given by npci)
                # "connected_banking": false
            }
        }
        
        r = requests.post(HYPTO_INITIATE_FUNDS_TRANSFER_URL, 
                        data=json.dumps(payload),
                        headers={
                            "Content-Type":"application/json", 
                            "Authorization": "Basic " + str(HYPTO_AUTH_TOKEN)  #WHAT IS BASIC?
                        })
        print(r.json())
        if r.status_code != 200 or "id" not in r.json():
            return JsonResponse(data={"message": "Insufficient Balance or Network error or invalid characters"}, status=400)
        
        transaction.debit_status = 5  #have to create credit_status or make new debit status
        transaction.save()
        return JsonResponse(data={"message": "transfer success"}, status=200)  #where do we store the response object? how to show res data here?
    except ObjectDoesNotExist:
        return JsonResponse(data={"message": "Invalid Transaction Id or Network error"}, status=404)

