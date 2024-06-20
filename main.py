import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread
import pickle
from pathlib import Path
import bcrypt
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(layout="wide")

# Initialize Cookie Manager
cookies = EncryptedCookieManager(
    prefix="myapp", 
    password="my_secret_password"
)
if not cookies.ready():
    st.stop()

# Function to load hashed passwords
def load_hashed_passwords():
    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)
    return hashed_passwords

# Function to verify password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

# Google Sheets authentication
SERVICE_ACCOUNT_FILE = 'excel.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1k4UVgLa00Hqa7le3QPbwQMSXwpnYPlvcEQTxXqTEY4U'
SHEET_NAME_1 = 'ZP dane kont'
SHEET_NAME_2 = 'ZP status'

# Authenticate and initialize the Google Sheets client
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
sheet1 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_1)
sheet2 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_2)

# Fetch all clients
def fetch_clients():
    clients = []
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        clients.append(f"{row[1]} {row[0]} {row[3]}")
    return clients

# Fetch all clients as DataFrame
def fetch_clients_df():
    rows = sheet1.get_all_values()
    return pd.DataFrame(rows[1:], columns=rows[0])

# Function to check if the client already exists
def client_exists(first_name, last_name, phone):
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        if row[0] == first_name and row[1] == last_name and row[3] == phone:
            return True
    return False

# Function to add a new client to the Google Sheet
def add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, tax_id, spouse_tax_id):
    if client_exists(first_name, last_name, phone):
        st.error("Taki klient już istnieje")
        return

    new_row = [
        first_name,
        last_name,
        office,
        phone,
        email,
        marital_status,
        bank_account,
        swift,
        tax_office,
        tax_id,
        spouse_tax_id
    ]
    sheet1.append_row(new_row)
    st.success("Nowy klient został dodany")

# Function to add a new service to the Google Sheet
def add_service(client, status_de, year, refund, guardian, remarks, informed, sent, fahrkosten, ubernachtung, entry_24h, entry_8h, entry_kabine, entry_ab_und_an, children, price, status, zapl, payment_method):
    new_row = [
        client,
        status_de,
        year,
        refund,
        guardian,
        remarks,
        informed,
        sent,
        fahrkosten,
        ubernachtung,
        entry_24h,
        entry_8h,
        entry_kabine,
        entry_ab_und_an,
        children,
        price,
        status,
        zapl,
        payment_method,
        datetime.now().strftime("%Y-%m-%d")
    ]
    sheet2.append_row(new_row)
    st.success("Nowa usługa została dodana")

# Function to fetch and filter services data
def fetch_services_data():
    rows = sheet2.get_all_values()[1:]  # Skip header row
    return rows

# Function to fetch the entire ZP status sheet data
def fetch_full_status_data():
    rows = sheet2.get_all_values()  # Include header row
    return pd.DataFrame(rows[1:], columns=rows[0])

# Function to update the ZP status sheet data
def update_status_data(df):
    sheet2.clear()
    sheet2.append_row(df.columns.tolist())
    for row in df.values.tolist():
        sheet2.append_row(row)

# Make column names unique
def make_unique_columns(df):
    columns = pd.Series(df.columns)
    for dup in columns[columns.duplicated()].unique():
        columns[columns[columns == dup].index.values.tolist()] = [f'{dup}_{i}' for i in range(sum(columns == dup))]
    df.columns = columns
    return df

# Main application
def main():
    st.title("System Zarządzania Klientami")

    # Opcja logowania
    hashed_passwords = load_hashed_passwords()
    usernames = ["kkamil", "bbeata"]  # Lista nazw użytkowników
    username = st.sidebar.text_input("Nazwa użytkownika")
    password = st.sidebar.text_input("Hasło", type="password")

    if st.sidebar.button("Zaloguj się"):
        if username in usernames:
            user_index = usernames.index(username)
            if verify_password(hashed_passwords[user_index], password):
                st.sidebar.success("Zalogowano pomyślnie")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                cookies.set("logged_in", True)
                cookies.set("username", username)
            else:
                st.sidebar.error("Błędne hasło")
        else:
            st.sidebar.error("Błędna nazwa użytkownika")

    if st.sidebar.button("Wyloguj się"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        cookies.delete("logged_in")
        cookies.delete("username")
        st.sidebar.info("Wylogowano")

    if cookies.get("logged_in") and not st.session_state.get("logged_in"):
        st.session_state["logged_in"] = cookies.get("logged_in")
        st.session_state["username"] = cookies.get("username")

    if st.session_state.get("logged_in"):
        menu = ["Dodaj klienta", "Dodaj usługę", "Podsumowanie", "Cały excel"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Dodaj klienta":
            st.subheader("Dodaj nowego klienta")

            with st.form(key="add_client_form"):
                first_name = st.text_input("Imię")
                last_name = st.text_input("Nazwisko")
                office = st.selectbox("Biuro", ["Przeworsk", "Jarosław"])
                phone = st.text_input("Nr telefonu")
                email = st.text_input("Email")
                marital_status = st.selectbox("Stan cywilny", ["kawaler", "żonaty", "rozwiedziony", "panienka", "mężatka"])
                bank_account = st.text_input("Nr konta bank")
                swift = st.text_input("SWIFT")
                tax_office = st.text_input("Finanzamt")
                tax_id = st.text_input("Nr ID")
                spouse_tax_id = st.text_input("Nr ID małżonka")

                submit_button = st.form_submit_button(label="Dodaj klienta")

            if submit_button:
                add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, tax_id, spouse_tax_id)
            
            # Display table of all clients
            clients_df = fetch_clients_df()
            st.subheader("Lista Klientów")
            st.dataframe(clients_df)

        elif choice == "Dodaj usługę":
            st.subheader("Dodaj nową usługę")

            all_clients = fetch_clients()

            with st.form(key="add_service_form"):
                client = st.selectbox("Klient", all_clients)
                status_de = st.selectbox("Status DE", ["DE - Otrzymano dokumenty", "DE - Rozliczono", "DE - Niekompletny zestaw"])
                year = st.selectbox("Rok", [str(year) for year in range(2019, datetime.now().year)])
                refund = st.text_input("Zwrot")
                guardian = st.selectbox("Opiekun", ["Kamil", "Beata", "Kasia"])
                remarks = st.text_area("Uwagi")
                informed = st.selectbox("Poinformowany", ["Tak", "Nie"])
                sent = st.selectbox("Wysłane", ["Tak", "Nie"])
                fahrkosten = st.text_input("Fahrkosten")
                ubernachtung = st.text_input("Übernachtung")
                entry_24h = st.text_input("24h")
                entry_8h = st.text_input("8h")
                entry_kabine = st.text_input("Kabine")
                entry_ab_und_an = st.text_input("Ab und an")
                children = st.text_area("Dzieci")
                price = st.selectbox("Cena", ["250", "400"])
                status = st.selectbox("Status", ["Opłacony", "Nieopłacony"])
                zapl = st.text_input("Zapłacono")
                payment_method = st.selectbox("Metoda płatności", ["Przelew", "Gotówka"])

                submit_button = st.form_submit_button(label="Dodaj usługę")

            if submit_button:
                add_service(client, status_de, year, refund, guardian, remarks, informed, sent, fahrkosten, ubernachtung, entry_24h, entry_8h, entry_kabine, entry_ab_und_an, children, price, status, zapl, payment_method)

        elif choice == "Podsumowanie":
            st.subheader("Podsumowanie")

            services_df = fetch_full_status_data()

            # Change background colors based on status
            def highlight_rows(row):
                color = 'white'
                if row['Status DE'] == 'DE - Otrzymano dokumenty':
                    color = 'lightgreen'
                elif row['Status DE'] == 'DE - Niekompletny zestaw':
                    color = 'lightcoral'
                return ['background-color: {}'.format(color)] * len(row)

            styled_df = services_df.style.apply(highlight_rows, axis=1)
            st.dataframe(styled_df)

            # Clients to inform or send
            
            inform_or_send_df = services_df[(services_df['Poinf'] == 'Nie') | (services_df['Wysł'] == 'Nie')]
            st.subheader("Klienci do poinformowania lub wysłania")
            st.dataframe(inform_or_send_df)
            styled_df = services_df.style.apply(highlight_rows)

            # Clients with advance payment
            advance_payment_df = services_df[services_df['Status płatności'] == 'Zaliczka']
            st.subheader("Klienci z zaliczką")
            st.dataframe(advance_payment_df)

        elif choice == "Cały excel":
            services_df = fetch_full_status_data()
            st.dataframe(services_df)

if __name__ == "__main__":
    main()
