from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

from storage import (
    load_data,
    save_data,
    hash_password,
    check_password
)

from notifications import send_notification


Window.clearcolor = (0.05, 0.06, 0.09, 1)

data = load_data()


# =========================================================
# ابزارهای کمکی
# =========================================================

def now():
    return datetime.now().strftime("%Y/%m/%d - %H:%M")


def money(value):
    return f"{value:,} تومان"


def make_button(text, height=55):
    button = Button(
        text=text,
        size_hint_y=None,
        height=dp(height)
    )
    return button


def make_input(hint="", password=False):
    return TextInput(
        hint_text=hint,
        password=password,
        multiline=False,
        size_hint_y=None,
        height=dp(55)
    )


# =========================================================
# صفحه راه‌اندازی اولیه
# =========================================================

class SetupScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(12)
        )

        title = Label(
            text="راه‌اندازی برنامه",
            font_size=dp(30),
            size_hint_y=None,
            height=dp(65)
        )

        root.add_widget(title)

        self.name = make_input("نام شما")
        self.balance = make_input("موجودی اولیه")
        self.password = make_input("رمز ورود", True)
        self.password2 = make_input("تکرار رمز", True)

        root.add_widget(self.name)
        root.add_widget(self.balance)
        root.add_widget(self.password)
        root.add_widget(self.password2)

        button = make_button("شروع کار")

        button.bind(on_press=self.setup)

        root.add_widget(button)

        self.add_widget(root)

    def setup(self, instance):

        name = self.name.text.strip()
        balance = self.balance.text.strip()
        password = self.password.text
        password2 = self.password2.text

        if not name:
            show_popup("خطا", "نام را وارد کنید.")
            return

        if not balance.isdigit():
            show_popup("خطا", "موجودی باید عدد باشد.")
            return

        if len(password) < 4:
            show_popup("خطا", "رمز باید حداقل ۴ رقم باشد.")
            return

        if password != password2:
            show_popup("خطا", "رمزها یکسان نیستند.")
            return

        data["setup_done"] = True
        data["name"] = name
        data["balance"] = int(balance)
        data["password_hash"] = hash_password(password)

        save_data(data)

        self.manager.current = "home"


# =========================================================
# صفحه ورود
# =========================================================

class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(30),
            spacing=dp(15)
        )

        title = Label(
            text="🔐 مدیریت موجودی",
            font_size=dp(30),
            size_hint_y=None,
            height=dp(70)
        )

        root.add_widget(title)

        self.password = make_input(
            "رمز ورود",
            True
        )

        root.add_widget(self.password)

        login = make_button("ورود")

        login.bind(
            on_press=self.login
        )

        root.add_widget(login)

        self.add_widget(root)

    def login(self, instance):

        if check_password(
            self.password.text,
            data["password_hash"]
        ):

            self.password.text = ""
            self.manager.current = "home"

        else:

            show_popup(
                "رمز اشتباه",
                "رمز ورود صحیح نیست."
            )


# =========================================================
# صفحه اصلی
# =========================================================

class HomeScreen(Screen):

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        # نوار بالا

        top = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(5)
        )

        goals = make_button("🎯 اهداف")

        goals.bind(
            on_press=lambda x:
            setattr(
                self.manager,
                "current",
                "goals"
            )
        )

        lock = make_button("🔒 قفل")

        lock.bind(
            on_press=lambda x:
            setattr(
                self.manager,
                "current",
                "login"
            )
        )

        top.add_widget(goals)
        top.add_widget(lock)

        root.add_widget(top)

        # سلام

        root.add_widget(
            Label(
                text=f"سلام {data['name']} 👋",
                font_size=dp(22),
                size_hint_y=None,
                height=dp(45)
            )
        )

        # موجودی

        root.add_widget(
            Label(
                text="موجودی فعلی",
                font_size=dp(20),
                size_hint_y=None,
                height=dp(40)
            )
        )

        root.add_widget(
            Label(
                text=money(data["balance"]),
                font_size=dp(38),
                size_hint_y=None,
                height=dp(75)
            )
        )

        # دکمه ها

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(65),
            spacing=dp(10)
        )

        minus = make_button("−")
        plus = make_button("+")

        minus.font_size = dp(35)
        plus.font_size = dp(35)

        minus.bind(
            on_press=lambda x:
            self.change_money(-1)
        )

        plus.bind(
            on_press=lambda x:
            self.change_money(1)
        )

        buttons.add_widget(minus)
        buttons.add_widget(plus)

        root.add_widget(buttons)

        root.add_widget(
            Label(
                text="تراکنش‌ها",
                font_size=dp(22),
                size_hint_y=None,
                height=dp(45)
            )
        )

        # لیست

        transactions = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None
        )

        transactions.bind(
            minimum_height=transactions.setter("height")
        )

        for index in range(
            len(data["transactions"]) - 1,
            -1,
            -1
        ):

            transaction = data["transactions"][index]

            amount = transaction["amount"]

            sign = "+" if amount >= 0 else ""

            text = (
                f"{sign}{money(amount)}\n"
                f"{transaction['date']}"
            )

            row = BoxLayout(
                size_hint_y=None,
                height=dp(85),
                spacing=dp(5)
            )

            label = Label(
                text=text
            )

            edit = make_button("ویرایش", 80)
            delete = make_button("حذف", 80)

            edit.bind(
                on_press=lambda x, i=index:
                self.edit_transaction(i)
            )

            delete.bind(
                on_press=lambda x, i=index:
                self.delete_transaction(i)
            )

            row.add_widget(label)
            row.add_widget(edit)
            row.add_widget(delete)

            transactions.add_widget(row)

        root.add_widget(transactions)

        self.add_widget(root)

    # -----------------------------------------------------

    def change_money(self, direction):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        amount = make_input("مبلغ")

        root.add_widget(amount)

        save = make_button("ثبت")

        root.add_widget(save)

        popup = Popup(
            title="مبلغ را وارد کنید",
            content=root,
            size_hint=(0.85, 0.4)
        )

        def submit(instance):

            value = amount.text.strip()

            if not value.isdigit() or int(value) <= 0:
                show_popup(
                    "خطا",
                    "یک مبلغ صحیح وارد کنید."
                )
                return

            value = int(value) * direction

            data["balance"] += value

            data["transactions"].append({
                "amount": value,
                "date": now()
            })

            save_data(data)

            popup.dismiss()

            self.check_goals()

            self.refresh()

        save.bind(on_press=submit)

        popup.open()

    # -----------------------------------------------------

    def delete_transaction(self, index):

        transaction = data["transactions"][index]

        data["balance"] -= transaction["amount"]

        del data["transactions"][index]

        save_data(data)

        self.refresh()

    # -----------------------------------------------------

    def edit_transaction(self, index):

        transaction = data["transactions"][index]

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        amount = make_input(
            "مبلغ جدید"
        )

        amount.text = str(
            abs(transaction["amount"])
        )

        root.add_widget(amount)

        save = make_button("ذخیره")

        root.add_widget(save)

        popup = Popup(
            title="ویرایش تراکنش",
            content=root,
            size_hint=(0.85, 0.4)
        )

        def submit(instance):

            if not amount.text.isdigit():
                return

            new_amount = int(amount.text)

            if transaction["amount"] < 0:
                new_amount *= -1

            difference = (
                new_amount -
                transaction["amount"]
            )

            data["balance"] += difference

            transaction["amount"] = new_amount

            save_data(data)

            popup.dismiss()

            self.check_goals()
            self.refresh()

        save.bind(on_press=submit)

        popup.open()

    # -----------------------------------------------------

    def check_goals(self):

        for goal in data["goals"]:

            if (
                data["balance"] >= goal["amount"]
                and not goal["completed"]
            ):

                goal["completed"] = True

                send_notification(
                    "🎯 هدف تکمیل شد!",
                    f"به هدف «{goal['title']}» رسیدی."
                )

        save_data(data)


# =========================================================
# صفحه اهداف
# =========================================================

class GoalsScreen(Screen):

    def on_pre_enter(self):
        self.refresh()

    def refresh(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        back = make_button("← بازگشت")

        back.bind(
            on_press=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        root.add_widget(back)

        root.add_widget(
            Label(
                text="🎯 اهداف مالی",
                font_size=dp(28),
                size_hint_y=None,
                height=dp(60)
            )
        )

        add = make_button("+ هدف جدید")

        add.bind(
            on_press=self.add_goal
        )

        root.add_widget(add)

        goals = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )

        goals.bind(
            minimum_height=goals.setter("height")
        )

        for index, goal in enumerate(data["goals"]):

            current = data["balance"]

            target = goal["amount"]

            percent = int(
                min(
                    100,
                    (current / target) * 100
                )
            )

            status = (
                "✅ تکمیل شده"
                if goal["completed"]
                else "⏳ در حال انجام"
            )

            box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(150),
                spacing=dp(4)
            )

            box.add_widget(
                Label(
                    text=(
                        f"{goal['title']} | "
                        f"{money(target)}"
                    )
                )
            )

            progress = ProgressBar(
                max=100,
                value=percent
            )

            box.add_widget(progress)

            box.add_widget(
                Label(
                    text=(
                        f"{percent}% | "
                        f"تاریخ هدف: {goal['date']}\n"
                        f"{status}"
                    )
                )
            )

            delete = make_button("حذف هدف", 40)

            delete.bind(
                on_press=lambda x, i=index:
                self.delete_goal(i)
            )

            box.add_widget(delete)

            goals.add_widget(box)

        root.add_widget(goals)

        self.add_widget(root)

    # -----------------------------------------------------

    def add_goal(self, instance):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        title = make_input("نام هدف")

        amount = make_input(
            "مبلغ هدف"
        )

        date = make_input(
            "تاریخ هدف - مثال 1405/12/29"
        )

        root.add_widget(title)
        root.add_widget(amount)
        root.add_widget(date)

        save = make_button("ثبت هدف")

        root.add_widget(save)

        popup = Popup(
            title="هدف جدید",
            content=root,
            size_hint=(0.9, 0.65)
        )

        def submit(instance):

            if (
                not title.text.strip()
                or not amount.text.isdigit()
                or not date.text.strip()
            ):
                show_popup(
                    "خطا",
                    "همه اطلاعات هدف را وارد کنید."
                )
                return

            target = int(amount.text)

            goal = {
                "title": title.text.strip(),
                "amount": target,
                "date": date.text.strip(),
                "completed": (
                    data["balance"] >= target
                )
            }

            data["goals"].append(goal)

            save_data(data)

            popup.dismiss()

            self.refresh()

        save.bind(on_press=submit)

        popup.open()

    # -----------------------------------------------------

    def delete_goal(self, index):

        del data["goals"][index]

        save_data(data)

        self.refresh()


# =========================================================
# Popup عمومی
# =========================================================

def show_popup(title, message):

    popup = Popup(
        title=title,
        content=Label(
            text=message
        ),
        size_hint=(0.8, 0.3)
    )

    popup.open()


# =========================================================
# برنامه
# =========================================================

class MoneyApp(App):

    def build(self):

        manager = ScreenManager()

        manager.add_widget(
            SetupScreen(name="setup")
        )

        manager.add_widget(
            LoginScreen(name="login")
        )

        manager.add_widget(
            HomeScreen(name="home")
        )

        manager.add_widget(
            GoalsScreen(name="goals")
        )

        if data["setup_done"]:
            manager.current = "login"
        else:
            manager.current = "setup"

        return manager


MoneyApp().run()
