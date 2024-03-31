from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'
    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)


class Financial(Base):
    __tablename__ = 'financial'
    ticker = Column(String, primary_key=True)
    ebitda = Column(Float)
    sales = Column(Float)
    net_profit = Column(Float)
    market_price = Column(Float)
    net_debt = Column(Float)
    assets = Column(Float)
    equity = Column(Float)
    cash_equivalents = Column(Float)
    liabilities = Column(Float)


# Connect to the database
engine = create_engine('sqlite:////Users/sheparl/Documents/Calculator for Investors/Calculator for Investors/investor.db')
Session = sessionmaker(bind=engine)
session = Session()


# Create the tables in the database if they don't exist
Base.metadata.create_all(engine)


def main_menu():
    print("MAIN MENU")
    print("0 Exit")
    print("1 CRUD operations")
    print("2 Show top ten companies by criteria")


def crud_menu():
    print("CRUD MENU")
    print("0 Back")
    print("1 Create a company")
    print("2 Read a company")
    print("3 Update a company")
    print("4 Delete a company")
    print("5 List all companies")


def top_ten_menu():
    print("TOP TEN MENU")
    print("0 Back")
    print("1 List by ND/EBITDA")
    print("2 List by ROE")
    print("3 List by ROA")


def get_option(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        return -1


def main():
    print("Welcome to the Investor Program!")
    while True:
        main_menu()
        choice = input("Enter an option: ")
        if choice == "0":
            print("Have a nice day!")
            break
        elif choice == "1":
            while True:
                crud_menu()
                crud_choice = input("Enter an option: ")
                if crud_choice == "0":
                    break
                elif crud_choice == "1":
                    create_company()
                elif crud_choice == "2":
                    read_company()
                elif crud_choice == "3":
                    update_company()
                elif crud_choice == "4":
                    delete_company()
                elif crud_choice == "5":
                    list_all_companies()
                else:
                    print("Invalid option!")
        elif choice == "2":
            while True:
                top_ten_menu()
                option = get_option("Enter an option: ")
                if option == 0:
                    break
                elif 1 <= option <= 3:
                    print("Not implemented!")
                    break  # Go back to the main menu after implementing the feature
                else:
                    print("Invalid option!")
        else:
            print("Invalid option!")


def create_company():
    # Get user input for the new company
    ticker = input("Enter ticker (in the format 'MOON'): ")
    company_name = input("Enter company (in the format 'Moon Corp'): ")
    sector = input("Enter industries (in the format 'Technology'): ")
    ebitda = float(input("Enter ebitda (in the format '987654321'): "))
    sales = float(input("Enter sales (in the format '987654321'): "))
    net_profit = float(input("Enter net profit (in the format '987654321'): "))
    market_price = float(input("Enter market price (in the format '987654321'): "))
    net_debt = float(input("Enter net debt (in the format '987654321'): "))
    assets = float(input("Enter assets (in the format '987654321'): "))
    equity = float(input("Enter equity (in the format '987654321'): "))
    cash_equivalents = float(input("Enter cash equivalents (in the format '987654321'): "))
    liabilities = float(input("Enter liabilities (in the format '987654321'): "))

    # Check if the ticker already exists
    existing_company = session.query(Company).filter_by(ticker=ticker).first()
    if existing_company:
        print(f"A company with ticker '{ticker}' already exists.")
        # Optionally, ask if the user wants to update the existing company here
    else:
        # Create an instance of the Company class with the provided details
        new_company = Company(ticker=ticker, name=company_name, sector=sector)
        new_financial = Financial(
            ticker=ticker,
            ebitda=ebitda,
            sales=sales,
            net_profit=net_profit,
            market_price=market_price,
            net_debt=net_debt,
            assets=assets,
            equity=equity,
            cash_equivalents=cash_equivalents,
            liabilities=liabilities
        )

        # Add the new company to the session and commit it to the database
        session.add(new_company)
        session.add(new_financial)
        session.commit()

        print("Company created successfully!")

    # Close the session
    session.close()


def read_company():
    company_name = input("Enter company name: ")

    # Find companies matching the input name
    companies = session.query(Company).filter(Company.name.like(f"%{company_name}%")).all()

    # Check if any companies were found
    if not companies:
        print("Company not found!")
        return

    # List matching companies
    for idx, company in enumerate(companies, start=1):
        print(f"{idx}. {company.name} ({company.ticker})")

    # Get user input for which company to select
    try:
        company_number = int(input("Enter company number: "))
        selected_company = companies[company_number - 1]  # Adjust for zero-based index
    except (ValueError, IndexError):
        print("Invalid company number!")
        return

    # Get the financial data for the selected company using SQLAlchemy
    financial_data = session.query(Financial).filter(Financial.ticker == selected_company.ticker).one_or_none()

    if financial_data:
        # Calculate financial indicators
        p_e = financial_data.market_price / financial_data.net_profit if financial_data.net_profit else None
        p_s = financial_data.market_price / financial_data.sales if financial_data.sales else None
        p_b = financial_data.market_price / financial_data.assets if financial_data.assets else None
        nd_ebitda = financial_data.net_debt / financial_data.ebitda if financial_data.ebitda else None
        roe = financial_data.net_profit / financial_data.equity if financial_data.equity else None
        roa = financial_data.net_profit / financial_data.assets if financial_data.assets else None
        l_a = financial_data.liabilities / financial_data.assets if financial_data.assets else None

        # Print financial indicators
        print(f"Financial indicators for {selected_company.name} ({selected_company.ticker}):")
        print(f"P/E: {p_e}")
        print(f"P/S: {p_s}")
        print(f"P/B: {p_b}")
        print(f"ND/EBITDA: {nd_ebitda}")
        print(f"ROE: {roe}")
        print(f"ROA: {roa}")
        print(f"L/A: {l_a}")

    else:
        print("Financial data not found for the selected company.")


def update_company():
    print("Enter company name:")
    company_name = input("> ")
    companies = session.query(Company).filter(Company.name.like(f"%{company_name}%")).all()

    if not companies:
        print("Company not found!")
        return

    for index, company in enumerate(companies, start=1):
        print(f"{index} {company.name} (Ticker: {company.ticker})")

    print("Enter company number:")
    try:
        company_number = int(input("> ")) - 1
        selected_company = companies[company_number]
    except (ValueError, IndexError):
        print("Invalid company number!")
        return

    # Ask for the new values for financial data
    print("Enter ebitda (in the format '987654321'):")
    new_ebitda = float(input("> "))
    print("Enter sales (in the format '987654321'):")
    new_sales = float(input("> "))
    print("Enter net profit (in the format '987654321'):")
    new_net_profit = float(input("> "))
    print("Enter market price (in the format '987654321'):")
    new_market_price = float(input("> "))
    print("Enter net debt (in the format '987654321'):")
    new_net_debt = float(input("> "))
    print("Enter assets (in the format '987654321'):")
    new_assets = float(input("> "))
    print("Enter equity (in the format '987654321'):")
    new_equity = float(input("> "))
    print("Enter cash equivalents (in the format '987654321'):")
    new_cash_equivalents = float(input("> "))
    print("Enter liabilities (in the format '987654321'):")
    new_liabilities = float(input("> "))

    # Find and update the financial details
    financial_record = session.query(Financial).filter_by(ticker=selected_company.ticker).first()
    if financial_record:
        financial_record.ebitda = new_ebitda
        financial_record.sales = new_sales
        financial_record.net_profit = new_net_profit
        financial_record.market_price = new_market_price
        financial_record.net_debt = new_net_debt
        financial_record.assets = new_assets
        financial_record.equity = new_equity
        financial_record.cash_equivalents = new_cash_equivalents
        financial_record.liabilities = new_liabilities

        # Commit the changes
        session.commit()
        print("Company updated successfully!")
    else:
        print("Financial data for this company not found. Update aborted.")


def delete_company():
    company_name = input("Enter company name: ")
    companies = session.query(Company).filter(Company.name.like(f"%{company_name}%")).all()

    if not companies:
        print("Company not found!")
        return

    for index, company in enumerate(companies, start=1):
        print(f"{index}. {company.name} (Ticker: {company.ticker})")

    try:
        company_number = int(input("Enter company number: ")) - 1
        selected_company = companies[company_number]
        session.delete(selected_company)
        session.commit()
        print("Company deleted successfully!")
    except (ValueError, IndexError):
        print("Invalid company number!")


def list_all_companies():
    print("COMPANY LIST")
    companies = session.query(Company).order_by(Company.ticker).all()
    for company in companies:
        print(f"{company.ticker} - {company.name} - {company.sector}")


# Start the program
if __name__ == '__main__':
    main()
