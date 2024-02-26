from collections import UserDict
from datetime import datetime, timedelta

class FieldIsEmpty(Exception):

    def __init__(self, message = 'Field is empty') -> None:
        self.message = message
        super().__init__(self.message)

class PhoneError(Exception):

    def __init__(self, message = 'Phone error') -> None:
        self.message = message
        super().__init__(self.message)

class BirthdayIsAlreadySet(Exception):

    def __init__(self, message = 'Birthday is already set') -> None:
        self.message = message
        super().__init__(self.message)

class RecordIsAlreadyExist(Exception):

    def __init__(self, message = 'Record is already exist') -> None:
        self.message = message
        super().__init__(self.message)

class RecordIsNotExist(Exception):

    def __init__(self, message = 'Record is not exist') -> None:
        self.message = message
        super().__init__(self.message)

class InvalidDateFormat(Exception):

    def __init__(self, message = 'Invalid date format. Use DD.MM.YYYY') -> None:
        self.message = message
        super().__init__(self.message)

class Field:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):

    def __init__(self, value):
        name = str(value).strip()
        if len(name) > 0:
            self.name = name
            super().__init__(self.name)
        else:
            raise FieldIsEmpty('Name is empty')

    def get_name(self):
        return self.name

class Phone(Field):

    def __init__(self, value):
        phone = str(value).strip()
        if len(phone) == 10:
            self.phone = phone
            super().__init__(self.phone)
        else:
            raise PhoneError('Phone number must contain ten digits')

    def __eq__(self, __value: object) -> bool:
        return self.phone == __value.phone

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise InvalidDateFormat

class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_str):

        phone = Phone(phone_str)
        try:
            self.phones.index(phone)
        except:
            self.phones.append(phone)

    def find_phone(self, phone_str):

        phone = Phone(phone_str)
        try:
            return self.phones[self.phones.index(phone)]
        except:
            return None

    def delete_phone(self, phone_str):

        phone = Phone(phone_str)
        try:
            self.phones.pop(self.phones.index(phone))
        except:
            raise RecordIsNotExist(f'Phone {phone} is not exist')

    def edit_phone(self, phone_str, new_phone_str):

        phone     = Phone(phone_str)
        new_phone = Phone(new_phone_str)

        try:
            self.phones[self.phones.index(phone)] = new_phone
        except:
            raise RecordIsNotExist(f'Phone {phone} is not exist')

    def add_birthday(self, value):
        if self.birthday is None:
            self.birthday = Birthday(value)
        else:
            raise BirthdayIsAlreadySet

    def show_birthday(self):
        return 'None' if self.birthday is None else self.birthday.value.strftime("%d.%m.%Y")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    
    def add_record(self, record):

        if self.data.get(record.name.name) is None:
            self.data[record.name.name] = record
        else:
            raise RecordIsAlreadyExist

    def find(self, name):

        record = self.data.get(name)
        if record is None:
            raise RecordIsNotExist
        else:
            return record

    def delete(self, name):

        record = self.data.get(name)
        if record is None:
            raise RecordIsNotExist
        else:
            self.data.pop(name)

    def birthdays(self):

        today = datetime.today().date()
        first_day = today + timedelta(days = 1)
        last_day  = today + timedelta(days = 7)
        upcoming_birthdays = ""

        for name, record in self.data.items():
            if record.birthday is None:
                continue
            else:
                birthday = record.birthday.value.date()
                birthday_this_year = datetime(year = first_day.year, month = birthday.month, day = birthday.day).date()

                if birthday_this_year < first_day:
                    birthday_this_year = datetime(year = last_day.year, month = birthday.month, day = birthday.day).date()

                birthday_weekday = birthday_this_year.weekday()

                if (birthday_weekday == 5) or (birthday_weekday == 6):
                    birthday_this_year = birthday_this_year + timedelta(days = (7 - birthday_weekday))

                if first_day <= birthday_this_year <= last_day:
                    upcoming_birthdays = ("" if len(upcoming_birthdays) == 0 else upcoming_birthdays + "\n") + birthday_this_year.strftime("%d.%m.%Y") + "  " + str(record)

        return upcoming_birthdays

def input_error(func):

    def inner(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except KeyError:
            return "No such contact exists."
        except ValueError:
            return "Enter the argument for the command."
        except IndexError:
            return "Enter the argument for the command."
        except FieldIsEmpty as e:
            return e.message
        except PhoneError as e:
            return e.message
        except BirthdayIsAlreadySet as e:
            return e.message
        except RecordIsAlreadyExist as e:
            return e.message
        except RecordIsNotExist as e:
            return e.message
        except InvalidDateFormat as e:
            return e.message

    return inner

def parse_input(user_input):

    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()

    return cmd, *args

@input_error
def add_contact(args, book):

    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)

    return "Contact added."

@input_error
def change_contact(args, book):

    name, phone = args

    record = book.find(name)
    if record is None:
        return "No such contact exists."
    elif len(record.phones) == 0:
        return "No phone to change."
    else:
        record.edit_phone(record.phones[0].phone, phone)
        return "Contact changed."

@input_error
def get_contact(args, book):

    name = args[0]
    record = book.find(name)
    if record is None:
        return "No such contact exists."
    else:
        return record

@input_error
def all_contacts(book):

    if len(book) > 0:
        book_str = ""
        for name, record in book.data.items():
            book_str = ("" if len(book_str) == 0 else book_str + "\n") + str(record)
        return book_str
    else:
        return "The list of contacts is empty."

@input_error
def add_birthday(args, book):

    name, birthday = args

    record = book.find(name)
    if record is None:
        return "No such contact exists."
    else:
        record.add_birthday(birthday)
        return "Birthday added."

@input_error
def show_birthday(args, book):

    name = args[0]
    record = book.find(name)
    if record is None:
        return "No such contact exists."
    else:
        return "No information yet" if record.birthday.value is None else record.birthday.value.strftime("%d.%m.%Y")

@input_error
def birthdays(book):
    return book.birthdays()

def main():

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
            print(change_contact(args, book))
        elif command == "phone":
            print(get_contact(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()