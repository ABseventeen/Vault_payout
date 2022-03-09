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
                # Initiate payout from Hypto
                initiate_payout(request)
                
            if data["event"] == "nach.debit.failed":
                transaction.debit_status = 3 
                transaction.failure_reason = data["payload"]["nach_debit"]["failure_description"]
                transaction.save()
            return JsonResponse(data={"message": "Transaction details updated"}, status=200)
        else:
            return JsonResponse(data={"message": "Not in proper format"}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse(data={"message": "Transaction not found"}, status=200)
