# Niharika Payment Setup

Niharika supports UPI payment links and WhatsApp payment confirmation messages.

## Required Settings

Set these in:

`C:\Users\saran\niharika\niharika-secrets.ps1`

```powershell
$env:NIHARIKA_PAYMENT_PHONE = "919535173147"
$env:NIHARIKA_WHATSAPP_NUMBER = "918149869054"
$env:NIHARIKA_UPI_ID = "your-upi-id@bank"
```

`NIHARIKA_PAYMENT_PHONE` is the receiver phone number for reference.

`NIHARIKA_UPI_ID` must be the real UPI/VPA ID. A phone number alone is not always a valid UPI payment address.

## What Works Now

- Business signup creates a Rs. 500/month account.
- If `NIHARIKA_UPI_ID` is set, the signup result shows a UPI payment button.
- If `NIHARIKA_WHATSAPP_NUMBER` is set, the signup result shows a WhatsApp payment confirmation button.
- Survey submissions can also send details to WhatsApp.

## Fully Automatic Activation

Plain UPI links cannot reliably confirm payment automatically inside this app.

For automatic account activation after payment, connect one of:

- Razorpay Subscriptions with webhook
- PhonePe payment gateway with webhook
- PayU/Cashfree payment gateway with webhook

Until a verified gateway webhook is connected, keep `payment_status` activation under admin control.
