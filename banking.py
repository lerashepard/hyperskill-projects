import sqlite3
import random

# Initialize SQLite database
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
            );''')
conn.commit()


def check_luhn_algorithm(card_number):
    nums = [int(x) for x in card_number]
    checksum = 0
    for i in range(len(nums)):
        if (i + 1) % 2 != 0:
            nums[i] *= 2
            if nums[i] > 9:
                nums[i] -= 9
    return sum(nums) % 10 == 0


def create_account():
    iin = "400000"
    acc_number = str(random.randint(100000000, 999999999))
    temp_card = iin + acc_number
    checksum = 0
    nums = [int(x) for x in temp_card]
    for i in range(len(nums)):
        if (i + 1) % 2 != 0:
            nums[i] *= 2
            if nums[i] > 9:
                nums[i] -= 9
    checksum = (10 - sum(nums) % 10) % 10
    card_number = temp_card + str(checksum)
    pin = str(random.randint(1000, 9999))

    cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", (card_number, pin))
    conn.commit()

    print(f"Your card has been created")
    print(f"Your card number:\n{card_number}")
    print(f"Your card PIN:\n{pin}")



def log_into_account():
    card_input = input("Enter your card number:")
    pin_input = input("Enter your PIN:")

    cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?", (card_input, pin_input))
    account = cur.fetchone()

    if account:
        print("You have successfully logged in!")
        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice = input()
            if choice == "1":
                cur.execute("SELECT balance FROM card WHERE number = ?", (card_input,))
                balance = cur.fetchone()[0]
                print(f"Balance: {balance}")
            elif choice == "2":
                income = int(input("Enter income:"))
                cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (income, card_input))
                conn.commit()
                print("Income was added!")
            elif choice == "3":
                print("Transfer")
                to_card = input("Enter card number:")
                if to_card == card_input:
                    print("You can't transfer money to the same account!")
                elif not check_luhn_algorithm(to_card):
                    print("Probably you made a mistake in the card number. Please try again!")
                else:
                    cur.execute("SELECT number FROM card WHERE number = ?", (to_card,))
                    if cur.fetchone() is None:
                        print("Such a card does not exist.")
                    else:
                        amount = int(input("Enter how much money you want to transfer:"))
                        cur.execute("SELECT balance FROM card WHERE number = ?", (card_input,))
                        balance = cur.fetchone()[0]
                        if amount > balance:
                            print("Not enough money!")
                        else:
                            cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?", (amount, card_input))
                            cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (amount, to_card))
                            conn.commit()
                            print("Success!")
            elif choice == "4":
                cur.execute("DELETE FROM card WHERE number = ?", (card_input,))
                conn.commit()
                print("The account has been closed!")
                return
            elif choice == "5":
                print("You have successfully logged out!")
                return
            elif choice == "0":
                exit_program()
    else:
        print("Wrong card number or PIN!")


def exit_program():
    print("Bye!")
    conn.close()
    exit()


while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    main_choice = input()
    if main_choice == "1":
        create_account()
    elif main_choice == "2":
        log_into_account()
    elif main_choice == "0":
        exit_program()
