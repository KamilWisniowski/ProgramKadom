import streamlit as st
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pickle
from pathlib import Path
import bcrypt
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager
st.set_page_config(layout="wide")

# Inicjalizacja managera ciasteczek
cookies = EncryptedCookieManager(
    prefix="my_prefix",  # Zmień prefix na unikalny dla swojej aplikacji
    password="super_secret_password"  # Użyj silnego hasła do szyfrowania ciasteczek
)

if not cookies.ready():
    st.stop()

# Funkcja do załadowania zaszyfrowanych haseł
def load_hashed_passwords():
    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)
    return hashed_passwords

# Funkcja do weryfikacji hasła
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

# Google Sheets authentication
SERVICE_ACCOUNT_FILE = 'excel.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1k4UVgLa00Hqa7le3QPbwQMSXwpnYPlvcEQTxXqTEY4U'
SHEET_NAME_1 = 'ZP dane kont'
SHEET_NAME_2 = 'ZP status'

# Authenticate and initialize the Google Sheets client
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
client = gspread.authorize(credentials)
sheet1 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_1)
sheet2 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_2)

@st.cache_data
def fetch_clients():
    clients = []
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        clients.append(f"{row[1]} {row[0]} {row[3]}")
    return clients

# Function to check if the client already exists
def client_exists(first_name, last_name, phone):
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        if row[0] == first_name and row[1] == last_name and row[3] == phone:
            return True
    return False

# Function to add a new client to the Google Sheet
def add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office,steuernummer, tax_id, spouse_tax_id):
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
        steuernummer,
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
@st.cache_data
def fetch_services_data():
    rows = sheet2.get_all_values()[1:]  # Skip header row
    return rows

# Function to fetch the entire ZP status sheet data
@st.cache_data
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

    if "logged_in" not in cookies:
        cookies["logged_in"] = "False"

    if st.sidebar.button("Zaloguj się"):
        if username in usernames:
            user_index = usernames.index(username)
            if verify_password(hashed_passwords[user_index], password):
                st.sidebar.success("Zalogowano pomyślnie")
                cookies["logged_in"] = "True"
                cookies["username"] = username
                cookies.save()
            else:
                st.sidebar.error("Błędne hasło")
        else:
            st.sidebar.error("Błędna nazwa użytkownika")

    if cookies.get("logged_in") == "True":
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
                steuernummer = st.text_input("steuernummer")
                tax_id = st.text_input("Nr ID")
                spouse_tax_id = st.text_input("Nr ID małżonka")

                submit_button = st.form_submit_button(label="Dodaj klienta")

            if submit_button:
                add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, tax_id, spouse_tax_id)

        elif choice == "Dodaj usługę":
            st.subheader("Dodaj nową usługę")

            all_clients = fetch_clients()

            with st.form(key="add_service_form"):
                client = st.selectbox("Klient", all_clients)
                status_de = st.selectbox("Status DE", ["","DE - Otrzymano dokumenty", "DE - Rozliczono", "DE - Niekompletny zestaw"])
                year = st.selectbox("Rok", [2023,2022,2021,2020,2019,2018])
                refund = st.text_input("Zwrot")
                guardian = st.selectbox("Opiekun", ["Kamil", "Beata", "Kasia"])
                remarks = st.text_area("Uwagi")
                informed = st.selectbox("Poinformowany", ["Nie","Tak"])
                sent = st.selectbox("Wysłane", ["Nie","Tak"])
                fahrkosten = st.text_input("Fahrkosten")
                ubernachtung = st.text_input("Übernachtung")
                entry_24h = st.text_input("24h")
                entry_8h = st.text_input("8h")
                entry_kabine = st.text_input("Kabine")
                entry_ab_und_an = st.text_input("Ab und an")
                children = st.text_area("Dzieci")
                price = st.selectbox("Cena", ["","250", "400"])
                status = st.selectbox("Status", ["Nieopłacony","Opłacony", "Zaliczka"])
                zapl = st.text_input("Zapłacono")
                payment_method = st.selectbox("Metoda płatności", ["","Przelew", "Gotówka"])

                submit_button = st.form_submit_button(label="Dodaj usługę")

            if submit_button:
                add_service(client, status_de, year, refund, guardian, remarks, informed, sent, fahrkosten, ubernachtung, entry_24h, entry_8h, entry_kabine, entry_ab_und_an, children, price, status, zapl, payment_method)

        elif choice == "Podsumowanie":
            st.subheader("Podsumowanie")

            # Pobieranie danych
            total_clients = len(sheet1.get_all_values()) - 1  # Excluding header row
            services_data = fetch_services_data()
            total_services = len(services_data)

            # Filtracja danych
            incomplete_services = [s for s in services_data if s[1] == "DE - Niekompletny zestaw"]
            processed_services = [s for s in services_data if s[1] == "DE - Rozliczono"]
            received_docs_services = [s for s in services_data if s[1] == "DE - Otrzymano dokumenty"]

            uninformed_or_unsent = [s for s in services_data if s[6] == "Nie" or s[7] == "Nie"]
            downpayment_services = [s for s in services_data if s[16] == "Zaliczka"]

            # Wyświetlanie podsumowania
            summary_data = {
                "Liczba klientów": [total_clients],
                "Liczba zamówionych usług": [total_services],
                "Liczba usług z status 'DE - Niekompletny zestaw'": [len(incomplete_services)],
                "Liczba usług z status 'DE - Rozliczono'": [len(processed_services)],
                "Liczba usług z status 'DE - Otrzymano dokumenty'": [len(received_docs_services)]
            }
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df)

            st.subheader("Klienci z usługami 'DE - Otrzymano dokumenty'")
            if received_docs_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                num_columns = len(received_docs_services[0])
                received_docs_df = pd.DataFrame(received_docs_services, columns=[f"Column{i+1}" for i in range(num_columns)])
                st.dataframe(received_docs_df)

            st.subheader("Klienci z usługami 'DE - Niekompletny zestaw'")
            if incomplete_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                num_columns = len(incomplete_services[0])
                incomplete_services_df = pd.DataFrame(incomplete_services, columns=[f"Column{i+1}" for i in range(num_columns)])
                st.dataframe(incomplete_services_df)

            st.subheader("Klienci do wysłania")
            if uninformed_or_unsent:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 1, 2, 6, 7, 5]  # Indeksy kolumn 1, 2, 3, 5, 7
                uninformed_or_unsent_filtered = [[row[i] for i in selected_columns] for row in uninformed_or_unsent]
                uninformed_or_unsent_df = pd.DataFrame(uninformed_or_unsent_filtered, columns=["Imię i Nazwisko", "Status", "Rok", "Poinformowany", "Wysłany", "UWAGI"])
                
            def highlight_status(row):
                styles = ['' for _ in row]
                
                # Highlight the entire row based on "Status" column
                if row['Status'] == "DE - Niekompletny zestaw":
                    styles = ['background-color: lightcoral' for _ in row]
                elif row['Status'] == "DE - Rozliczono":
                    styles = ['background-color: yellow' for _ in row]
                elif row['Status'] == "DE - Otrzymano dokumenty":
                    styles = ['background-color: lightgreen' for _ in row]
                
                # Highlight specific cells in "Poinformowany" and "Wysłany" columns
                if row['Poinformowany'] == "Nie":
                    styles[3] = 'background-color: red; color: white;'
                if row['Wysłany'] == "Nie":
                    styles[4] = 'background-color: red; color: white;'
                
                return styles

            uninformed_or_unsent_styled = uninformed_or_unsent_df.style.apply(highlight_status, axis=1)
            st.dataframe(uninformed_or_unsent_styled)
            
            st.subheader("Klienci z zaliczką")
            if downpayment_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 15,16, 17, 18, 19,5, 20]  # Indeksy kolumn 1, 2, 3, 5, 7
                downpayment_services_filtered = [[row[i] for i in selected_columns] for row in downpayment_services]
                downpayment_services_df = pd.DataFrame(downpayment_services_filtered, columns=["Imię i Nazwisko","Cena", "Status płatności", "Zapłacono", "Forma zapłaty", "Nr. faktury", "Uwagi","Data wystawienia faktury"])
            st.dataframe(downpayment_services_df)
                

        elif choice == "Cały excel":
            st.subheader("Cały arkusz ZP status")
            df = fetch_full_status_data()
            df_unique = make_unique_columns(df)  # Ensure unique column names
            edited_df = st.data_editor(df_unique)

            if st.button("Zapisz zmiany"):
                update_status_data(edited_df)
                st.success("Dane zostały zaktualizowane")

    else:
        st.info("Proszę się zalogować")

if __name__ == "__main__":
    main()
