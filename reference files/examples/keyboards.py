from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardManager:
    @staticmethod
    def get_main_keyboard() -> InlineKeyboardMarkup:
        """Get the main keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("Add Pattern", callback_data="add_pattern"),
                InlineKeyboardButton("List Patterns", callback_data="list_patterns")
            ],
            [
                InlineKeyboardButton("Settings", callback_data="settings"),
                InlineKeyboardButton("Help", callback_data="help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 