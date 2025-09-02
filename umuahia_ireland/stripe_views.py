import stripe
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class DonationPageView(View):
    """Display the donation page with Stripe integration"""

    def get(self, request):
        context = {
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        }
        return render(request, "donations/donate.html", context)


@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout session for embedded donations"""
    try:
        data = json.loads(request.body)
        amount = int(float(data.get("amount", 10)) * 100)  # Convert to cents

        # Create Stripe checkout session for embedded checkout
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Donation to Umuahia Ireland Community",
                            "description": "Supporting the Nigerian community in Ireland",
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            ui_mode="embedded",
            return_url=request.build_absolute_uri("/") + "?donation=success",
            metadata={
                "donation_type": "community_support",
                "donor_email": data.get("email", ""),
                "donor_name": data.get("name", ""),
            },
        )

        return JsonResponse({"client_secret": checkout_session.client_secret})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def donation_success(request):
    """Handle successful donations"""
    messages.success(
        request,
        "Thank you for your generous donation! Your support helps strengthen our community.",
    )
    return render(request, "donations/success.html")


def donation_cancel(request):
    """Handle cancelled donations"""
    messages.info(request, "Donation was cancelled. You can try again anytime.")
    return render(request, "donations/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Get donation details
        amount = session["amount_total"] / 100  # Convert from cents
        donor_email = session["metadata"].get("donor_email", "")
        donor_name = session["metadata"].get("donor_name", "")

        # Here you can save donation records to your database
        # Example: Donation.objects.create(...)

        print(f"Donation completed: €{amount} from {donor_name} ({donor_email})")

    elif event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        print(f"PaymentIntent succeeded: {payment_intent['id']}")

    else:
        print(f'Unhandled event type: {event["type"]}')

    return HttpResponse(status=200)


# Quick donation functions for different amounts
def quick_donate(request, amount):
    """Quick donation with preset amounts using embedded checkout"""
    try:
        amount_cents = int(amount * 100)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": f"€{amount} Donation to Umuahia Ireland Community",
                            "description": "Supporting the Nigerian community in Ireland",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            ui_mode="embedded",
            return_url=request.build_absolute_uri("/") + "?donation=success",
            metadata={
                "donation_type": "quick_donation",
                "amount": str(amount),
            },
        )

        return JsonResponse({"client_secret": checkout_session.client_secret})

    except Exception as e:
        return JsonResponse(
            {"error": f"Error processing donation: {str(e)}"}, status=400
        )
