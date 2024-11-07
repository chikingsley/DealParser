# BotStream User Guide

This guide provides a step-by-step walkthrough of using the BotStream Telegram bot to manage affiliate deals.

## 1. Adding Deals

1.  **Open Telegram and find the BotStream bot.**
2.  **Send a message containing your affiliate deal information.** Use a clear format, including the following fields:
    *   `GEO`: (e.g., US, UK, CA)
    *   `Partner`: (e.g., AcmeCorp, BetaCo)
    *   `Price`: (e.g., $100, £50)
    *   `CR`: (Conversion Rate, e.g., 10%, 15%)
    *   `Sources`: (e.g., Google Ads, Facebook)

    Example:  `GEO: US Partner: AcmeCorp Price: $100 CR: 10% Sources: Google Ads`

3.  **The bot will process your message and display the parsed deal information.**  If multiple deals are detected in your message, you will be able to navigate between them.

## 2. Reviewing Deals

After the bot parses your deal information, you'll see a message displaying the details. Below the deal information, you'll find an inline keyboard with the following options:

*   **✅ Confirm:**  Tap this button to confirm that the deal information is correct.
*   **❌ Reject:** Tap this button to reject the deal if the information is incorrect.
*   **✏️ Edit:** Tap this button to edit any of the deal's fields.

## 3. Editing Deals

If you tap the "✏️ Edit" button, a new inline keyboard will appear, allowing you to modify individual fields:

*   Tap "GEO", "Partner", "Price", "CR", or "Sources" to edit the corresponding field.
*   After making your changes, the bot will update the deal information.
*   Tap "🔙 Back" to return to the deal review screen.

## 4. Navigating Multiple Deals

If your initial message contained multiple deals, you'll see navigation buttons on the inline keyboard:

*   **⬅️ Previous:** Tap to view the previous deal.
*   **➡️ Next:** Tap to view the next deal.

## 5. Advanced Features (for Administrators)

Administrators have access to additional features for managing patterns and bot settings.  These features will be documented separately.


This guide provides a clear and concise overview of the user interaction with the BotStream bot.  For more technical details, please refer to the bot's source code and the developer documentation.
