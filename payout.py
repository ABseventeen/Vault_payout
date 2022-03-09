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
                "reference_number": "transaction.digio_transaction_id",
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
