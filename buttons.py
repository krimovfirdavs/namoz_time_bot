from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

REGIONS = ["Andijon", "Urganch", "Toshkent"]


def region_btn():
    inlines = []
    btn_box = []
    for i in REGIONS:
        btn_box.append(InlineKeyboardButton(text=i, callback_data=f"{i}"))
        if len(btn_box) == 2:
            inlines.append(btn_box)
            btn_box = []
    inlines.append(btn_box)
    return InlineKeyboardMarkup(inline_keyboard=inlines)
