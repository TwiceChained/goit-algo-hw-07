from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)



class Name(Field):
    pass



class Phone(Field):
    def __init__(self,value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Incorrect phone number format. Number should be 10 digits long")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  # валідація формату DD.MM.YYYY
            self.value = value.strip()            # зберігаємо рядок
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name) # об’єкт Name.
        self.phones = [] # список об’єктів Phone.
        self.birthday = None


    def add_birthday(self, str_date):
        birthday = Birthday(str_date)
        self.birthday = birthday


    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)


    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone    
        return None 


    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number) 
        if phone:
            self.phones.remove(phone)


    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if not phone: 
                raise ValueError("Old phone not found")
        validated = Phone(new_phone)
        phone.value = validated.value 


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(phone.value for phone in self.phones)}"
    

    def birthday_str(self):
        return self.birthday.value if self.birthday else None



class AddressBook(UserDict):
    def add_record(self, record : Record):
        self.data[record.name.value] = record 

    def find(self, name_str):
        return self.data.get(name_str)

    def delete(self, name_str):
        if name_str in self.data:
            del self.data[name_str]
    
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    

    def get_upcoming_birthdays(self, days=7):
        today = date.today()
        out = []
        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            b_this = birthday.replace(year=today.year)
            if b_this < today:
                b_this = b_this.replace(year=today.year + 1)

            diff = (b_this - today).days
            if 0 <= diff <= days:
                greet = b_this
                while greet.weekday() >= 5:  # 5=сб, 6=нд
                    greet += timedelta(days=1)
                out.append({"name": record.name.value, "birthday": greet.strftime("%d.%m.%Y")})

        return out




def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            if func.__name__ in ("add_contact", "change_contact"):
                return "Give me name and phone please."
            if func.__name__ == "show_phone":
                return "Enter user name."
            return "Wrong arguments."

        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
        
    return inner



def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book):
    name, bday, *_ = args
    rec = book.find(name)
    if rec is None:
        rec = Record(name)
        book.add_record(rec)
    rec.add_birthday(bday)
    return "Birthday set."



@input_error
def show_birthday(args, book):
    name, *_ = args
    rec = book.find(name)
    if rec is None:    
        raise KeyError
    return rec.birthday.value if rec.birthday else "No birthday set."



@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{it['birthday']} — {it['name']}" for it in upcoming)







if __name__ == '__main__':

    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            name, old_p, new_p, *_ = args
            rec = book.find(name)
            if rec is None: print("Contact not found."); continue
            try:
                rec.edit_phone(old_p, new_p)
                print("Contact updated.")
            except ValueError as e:
                print(str(e))

        elif command == "phone":
            name, *_ = args
            rec = book.find(name)
            if rec is None: 
                print("Contact not found.")
            else:
                nums = ", ".join(p.value for p in rec.phones) or "No phones."
                print(nums)

        elif command == "all":
            if not book.data:
                print("No contacts found.")
            else:
                for rec in book.data.values():
                    phones = ", ".join(p.value for p in rec.phones) or "—"
                    bday = rec.birthday.value if rec.birthday else "—"
                    print(f"{rec.name.value}: {phones}; birthday: {bday}")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")
