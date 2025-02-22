import streamlit as st
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pickle
from pathlib import Path
import bcrypt
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager
import time

st.set_page_config(layout="wide")
# Cache to store fetched clients
clients_cache = None
last_fetch_time = 0

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
def add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office,steuernummer, tax_id, spouse_tax_id,Dataurodzenia,Religia,Ulica,Miejscowośc,Dataslubu,DataUrŻony,imiezony):
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
        spouse_tax_id,
        Dataurodzenia,
        Religia,
        Ulica,
        Miejscowośc,
        Dataslubu,
        DataUrŻony,
        imiezony
    ]
    sheet1.append_row(new_row)
    st.success("Nowy klient został dodany")

# Function to add a new service to the Google Sheet
def add_service(klient,statusDE,rok,zwrot,opiekun,uwagi,poinformowany,wyslany,fahrkosten,ubernachtung,h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc):
    new_row = [
        klient,
        statusDE,
        rok,zwrot,
        opiekun,
        uwagi,
        poinformowany,
        wyslany,
        fahrkosten,
        ubernachtung,
        h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc
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
    if row['Poinformowany'] == "Tak":
        styles[3] = 'background-color: green; color: white;'
    if row['Wysłany'] == "Tak":
        styles[4] = 'background-color: green; color: white;'
    return styles
def highlight_row_if_status(row):
    styles = ['' for _ in row]
    
    # Highlight the entire row based on "Status" column
    if row['Status'] == "DE - Niekompletny zestaw":
        styles = ['background-color: lightcoral' for _ in row]
    elif row['Status'] == "DE - Rozliczono":
        styles = ['background-color: yellow' for _ in row]
    elif row['Status'] == "DE - Otrzymano dokumenty":
        styles = ['background-color: lightgreen' for _ in row]
    return styles
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


        # Funkcja do resetowania formularza dodawania klienta
        def reset_client_form():
            st.session_state["office"] = "Przeworsk"
            st.session_state["first_name"] = ""
            st.session_state["last_name"] = ""
            st.session_state["phone"] = ""
            st.session_state["email"] = ""
            st.session_state["bank_account"] = ""
            st.session_state["swift"] = ""
            st.session_state["tax_office"] = ""
            st.session_state["steuernummer"] = ""
            st.session_state["tax_id"] = ""
            st.session_state["Dataurodzenia"] = ""
            st.session_state["Religia"] = ""
            st.session_state["Ulica"] = ""
            st.session_state["Miejscowośc"] = ""
            st.session_state["marital_status"] = ""
            st.session_state["Dataslubu"] = ""
            st.session_state["imiezony"] = ""
            st.session_state["spouse_tax_id"] = ""
            st.session_state["DataUrŻony"] = ""

        # Sekcja dodawania klienta
        if choice == "Dodaj klienta":
            st.subheader("Dodaj nowego klienta")

            # Przycisk do czyszczenia formularza
            if st.button("Wyczyść"):
                reset_client_form()

            # Ustawienie początkowego stanu
            
            marital_status2 = st.selectbox('Stan cywilny:', ['kawaler', 'żonaty', 'rozwiedziony', 'panienka', 'mężatka'])
            st.session_state["marital_status"] = marital_status2
             

            with st.form(key="client_info_form", border=False):
                office = st.selectbox("Biuro", ["Przeworsk", "Jarosław"], key="office")
                first_name = st.text_input("Imię", key="first_name")
                last_name = st.text_input("Nazwisko", key="last_name")
                phone = st.text_input("Nr telefonu", key="phone")
                email = st.text_input("Email", key="email")
                bank_account = st.text_input("Nr konta bank", key="bank_account")
                swift = st.text_input("SWIFT", key="swift")
                tax_office = st.text_input("Finanzamt", key="tax_office")
                steuernummer = st.text_input("Steuernummer", key="steuernummer")
                tax_id = st.text_input("Nr ID", key="tax_id")
                Dataurodzenia = st.text_input("Data urodzenia klienta", key="Dataurodzenia")
                Religia = st.selectbox("Religia", ["", "VD", "RK", "EV"], key="Religia")
                Ulica = st.text_input("Ulica zamieszkania klienta", key="Ulica")
                Miejscowośc = st.text_input("Kod pocztowy i miejscowość", key="Miejscowośc")         
                marital_status = st.text_input("Stan cywilny", key="marital_status",disabled=True)
                if marital_status2 == "żonaty":
                    st.session_state["marital_status2"] = "żonaty"

                    Dataslubu = st.text_input("Data ślubu", key="Dataslubu")
                    imiezony = st.text_input("Imię żony", key="imiezony")
                    spouse_tax_id = st.text_input("Nr ID małżonka", key="spouse_tax_id")
                    DataUrŻony = st.text_input("Data ur. żony", key="DataUrŻony")
                else:
                    Dataslubu = ""
                    imiezony = ""
                    spouse_tax_id = ""
                    DataUrŻony = ""
                submit_info = st.form_submit_button(label='Dodaj klienta')


            if submit_info:
                add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, steuernummer, tax_id, spouse_tax_id, Dataurodzenia, Religia, Ulica, Miejscowośc, Dataslubu, DataUrŻony, imiezony)
                


        # Funkcja do resetowania formularza dodawania usługi
        def reset_service_form():
            st.session_state["klient"] = "  "
            st.session_state["statusDE"] = ""
            st.session_state["rok"] = "2023"
            st.session_state["opiekun"] = "Kamil"
            st.session_state["uwagi"] = ""
            st.session_state["poinformowany"] = "Nie"
            st.session_state["wyslany"] = "Nie"
            st.session_state["fahrkosten"] = ""
            st.session_state["ubernachtung"] = ""
            st.session_state["h24"] = ""
            st.session_state["h8"] = ""
            st.session_state["wKabinie"] = ""
            st.session_state["anUndAb"] = ""
            st.session_state["dzieci"] = ""
            st.session_state["cena"] = ""
            st.session_state["statusPlatnosciu"] = "Nieopłacony"
            st.session_state["zaplacono"] = ""
            st.session_state["formaZaplaty"] = ""
            st.session_state["nrfaktury"] = ""
            st.session_state["dataWystawieniaFaktury"] = ""
            st.session_state["zarobkiMezaEuro"] = ""
            st.session_state["zarobZonyEuro"] = ""
            st.session_state["nr22"] = ""
            st.session_state["nr23"] = ""
            st.session_state["nr25"] = ""
            st.session_state["nr26"] = ""
            st.session_state["nr27"] = ""
            st.session_state["pracodawca"] = ""
            st.session_state["chorobowe"] = ""
            st.session_state["klasaPIT1"] = ""
            st.session_state["brutto1"] = ""
            st.session_state["podatek1"] = ""
            st.session_state["dopłata1"] = ""
            st.session_state["kościelny1"] = ""
            st.session_state["kurzarbeitergeld1"] = ""
            st.session_state["klasaPIT2"] = ""
            st.session_state["brutto2"] = ""
            st.session_state["podatek2"] = ""
            st.session_state["dopłata2"] = ""
            st.session_state["kościelny2"] = ""
            st.session_state["kurzarbeitergeld2"] = ""
            st.session_state["klasaPIT3"] = ""
            st.session_state["brutto3"] = ""
            st.session_state["podatek3"] = ""
            st.session_state["dopłata3"] = ""
            st.session_state["kościelny3"] = ""
            st.session_state["kurzarbeitergeld3"] = ""
            st.session_state["kontoElster"] = "Nie"
            st.session_state["ogrObPodatkowy"] = ""
            st.session_state["aktualny_stan_zamieszkania"] = ""
            st.session_state["miejsce_urodzenia"] = ""
            st.session_state["kraj_urodzenia"] = ""
            st.session_state["narodowosc"] = ""

        # Sekcja dodawania usługi
        if choice == "Dodaj usługę":
            st.subheader("Dodaj nową usługę")

            # Przycisk do czyszczenia formularza
            if st.button("Wyczyść"):
                reset_service_form()
            st.subheader("Zaznacz odpowiednie opcje")

            all_clients = fetch_clients()
            ogrObPodatkowy2 = st.selectbox("Ograniczony obowiązek podatkowy", ["Nie", "Tak"], key="ogrObPodatkowy2")
            zarobkiwPolsce = st.checkbox("Zaznacz, aby dodać zarobki w Polsce", key="zarobkiwPolsce")
            dodatkowe = st.checkbox("Zaznacz, aby dodać pola 22, 23, 25, 26, 27, pracodawca, chorobowe", key="dodatkowe")
            CzyJestPit1 = st.checkbox("PIT nr. 1 (Zaznaczyć, jeżeli klient posiada) ", key="CzyJestPit1")
            CzyJestPit2 = st.checkbox("PIT nr. 2 (Zaznaczyć, jeżeli klient posiada)", key="CzyJestPit2")
            CzyJestPit3 = st.checkbox("PIT nr. 3 (Zaznaczyć, jeżeli klient posiada)", key="CzyJestPit3")
            formaZaplaty2 = st.selectbox("Metoda płatności", ["", "Przelew", "Gotówka", "Faktura"], key="formaZaplaty2")

            st.session_state["ogrObPodatkowy"] = ogrObPodatkowy2
            st.session_state["formaZaplaty"] = formaZaplaty2
             
            st.subheader("Wypełnij dane usługi")

            with st.form(key="status_form", border=False):
                
                klient = st.selectbox("Klient", all_clients, key="klient")
                statusDE = st.selectbox("Status DE", ["", "DE - Otrzymano dokumenty", "DE - Rozliczono", "DE - Niekompletny zestaw"], key="statusDE")
                rok = st.selectbox("Rok", ['2024','2023', '2022', '2021', '2020', '2019', '2018'], key="rok")
                opiekun = st.selectbox("Opiekun", ["Kamil", "Beata", "Kasia"], key="opiekun")
                uwagi = st.text_area("Uwagi", key="uwagi")
                poinformowany = st.selectbox("Poinformowany", ["Nie", "Tak"], key="poinformowany")
                wyslany = st.selectbox("Wysłane", ["Nie", "Tak"], key="wyslany")
                fahrkosten = st.text_input("Fahrkosten", key="fahrkosten")
                ubernachtung = st.text_input("Übernachtung", key="ubernachtung")
                h24 = st.text_input("24h", key="h24")
                h8 = st.text_input("8h", key="h8")
                wKabinie = st.text_input("Kabine", key="wKabinie")
                anUndAb = st.text_input("Ab und an", key="anUndAb")
                dzieci = st.text_area("Dzieci", key="dzieci")
                cena = st.selectbox("Cena", ["", "250", "400"], key="cena")
                statusPlatnosciu = st.selectbox("Status", ["Nieopłacony", "Opłacony", "Zaliczka"], key="statusPlatnosciu")
                zaplacono = st.text_input("Zapłacono", key="zaplacono")
                zwrot = ""
                formaZaplaty = st.text_input("Metoda płatności", key="formaZaplaty", disabled=True)
                if formaZaplaty == "Faktura":
                    nrfaktury = st.text_input("Nr. Faktury", key="nrfaktury")
                    dataWystawieniaFaktury = st.text_input("Data wystawienia faktury", key="dataWystawieniaFaktury")                
                else:
                    nrfaktury = ""
                    dataWystawieniaFaktury = ""
                kontoElster = st.selectbox("kontoElster", ["Nie", "Tak"], key="kontoElster")                  
                ogrObPodatkowy = st.selectbox("ogrObPodatkowy", ["Nie", "Tak"], key="ogrObPodatkowy",disabled=True)
                
                if ogrObPodatkowy == "Tak":
                    aktualny_stan_zamieszkania = st.text_input("aktualny_stan_zamieszkania", key="aktualny_stan_zamieszkania")
                    miejsce_urodzenia = st.text_input("miejsce_urodzenia", key="miejsce_urodzenia")
                    kraj_urodzenia = st.text_input("kraj_urodzenia", key="kraj_urodzenia")
                    narodowosc = st.text_input("narodowosc", key="narodowosc")                 
                else:
                    aktualny_stan_zamieszkania = ""
                    miejsce_urodzenia = ""
                    kraj_urodzenia = ""
                    narodowosc = ""

                

                if zarobkiwPolsce:
                    zarobkiMezaEuro = st.text_input("Zarobki męża", key="zarobkiMezaEuro")
                    zarobZonyEuro = st.text_input("zarobZonyEuro", key="zarobZonyEuro")            
                else:
                    zarobkiMezaEuro = ""
                    zarobZonyEuro = ""

                if dodatkowe:
                    nr22 = st.text_input("nr22", key="nr22")
                    nr23 = st.text_input("nr23", key="nr23")
                    nr25 = st.text_input("nr25", key="nr25")
                    nr26 = st.text_input("nr26", key="nr26")
                    nr27 = st.text_input("nr27", key="nr27")
                    pracodawca = st.text_input("pracodawca", key="pracodawca")
                    chorobowe = st.text_input("chorobowe", key="chorobowe")
                else:
                    nr22 = ""
                    nr23 = ""
                    nr25 = ""
                    nr26 = ""
                    nr27 = ""
                    pracodawca = ""
                    chorobowe = ""

                if CzyJestPit1:
                    klasaPIT1 = st.text_input("klasaPIT1", key="klasaPIT1")
                    brutto1 = st.text_input("brutto1", key="brutto1")
                    podatek1 = st.text_input("podatek1", key="podatek1")
                    dopłata1 = st.text_input("dopłata1", key="dopłata1")
                    kościelny1 = st.text_input("kościelny1", key="kościelny1")
                    kurzarbeitergeld1 = st.text_input("kurzarbeitergeld1", key="kurzarbeitergeld1")
                else:
                    klasaPIT1 = ""
                    brutto1 = ""
                    podatek1 = ""
                    dopłata1 = ""
                    kościelny1 = ""
                    kurzarbeitergeld1 = ""
                    
                if CzyJestPit2:    
                    klasaPIT2 = st.text_input("klasaPIT2", key="klasaPIT2")
                    brutto2 = st.text_input("brutto2", key="brutto2")
                    podatek2 = st.text_input("podatek2", key="podatek2")
                    dopłata2 = st.text_input("dopłata2", key="dopłata2")
                    kościelny2 = st.text_input("kościelny2", key="kościelny2")
                    kurzarbeitergeld2 = st.text_input("kurzarbeitergeld2", key="kurzarbeitergeld2")
                else:
                    klasaPIT2 = ""
                    brutto2 = ""
                    podatek2 = ""
                    dopłata2 = ""
                    kościelny2 = ""
                    kurzarbeitergeld2 = ""
                if CzyJestPit3:   
                    klasaPIT3 = st.text_input("klasaPIT3", key="klasaPIT3")
                    brutto3 = st.text_input("brutto3", key="brutto3")
                    podatek3 = st.text_input("podatek3", key="podatek3")
                    dopłata3 = st.text_input("dopłata3", key="dopłata3")
                    kościelny3 = st.text_input("kościelny3", key="kościelny3")
                    kurzarbeitergeld3 = st.text_input("kurzarbeitergeld3", key="kurzarbeitergeld3")
                else:
                    klasaPIT3 = ""
                    brutto3 = ""
                    podatek3 = ""
                    dopłata3 = ""
                    kościelny3 = ""
                    kurzarbeitergeld3 = ""
                submit_status = st.form_submit_button(label='Dodaj usługę')
            if submit_status:
                if not klient or not statusDE or not rok:
                    st.error("Podanie danych klienta, Statusu DE oraz roku rozliczenia jest wymagane")
                else:
                    add_service(klient,statusDE,rok,zwrot,opiekun,uwagi,poinformowany,wyslany,fahrkosten,ubernachtung,h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc)
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


            uninformed_or_unsent = [s for s in services_data if (s[6] == "Nie" or s[7] == "Nie") and s[1] == "DE - Rozliczono"]
            downpayment_services = [s for s in services_data if s[16] == "Zaliczka"]

            # Wyświetlanie podsumowania w kafelkach
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Liczba klientów", value=total_clients)
            with col2:
                st.metric(label="Liczba zamówionych usług", value=total_services)
            with col3:
                st.metric(label="Usługi 'DE - Niekompletny zestaw'", value=len(incomplete_services))
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.metric(label="Usługi 'DE - Rozliczono'", value=len(processed_services))
            with col5:
                st.metric(label="Usługi 'DE - Otrzymano dokumenty'", value=len(received_docs_services))
            with col6:
                st.metric(label="Do wysłania", value=len(uninformed_or_unsent))

            #Klienci z usługami 'DE - Otrzymano dokumenty'
            if received_docs_services:
                selected_columns = [0, 1, 2, 4, 5, 48,49]  # Indeksy kolumn 1, 2, 3, 5, 7
                received_docs_services_filtered = [[row[i] for i in selected_columns] for row in received_docs_services]
                received_docs_df = pd.DataFrame(received_docs_services_filtered, columns=["Imię i Nazwisko", "Status", "Rok", "Opiekun", "UWAGI", "Konto Elster", "Ogr. ob. podatkowy"])
                # Numerowanie wierszy od 1
                received_docs_df.index = received_docs_df.index + 1
                

            st.markdown(f"<h3 style='color: #545454; font-weight:600;font-size:20px'>Klienci z usługami <span style='color: #03ab0f; font-weight:700;font-size:30px'>DE - Otrzymano dokumenty</span> (ilość: {len(received_docs_df)})</h3>", unsafe_allow_html=True)
            received_docs_services_styled = received_docs_df.style.apply(highlight_row_if_status, axis=1)
            st.dataframe(received_docs_services_styled)
            
            #Klienci z usługami 'DE - Niekompletny zestaw'
            if incomplete_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 1, 2, 4, 5, 48,49]  # Indeksy kolumn 1, 2, 3, 5, 7
                incomplete_services_filtered = [[row[i] for i in selected_columns] for row in incomplete_services]
                incomplete_services_df = pd.DataFrame(incomplete_services_filtered, columns=["Imię i Nazwisko", "Status", "Rok", "Opiekun", "UWAGI", "Konto Elster", "Ogr. ob. podatkowy"])
                # Numerowanie wierszy od 1
                incomplete_services_df.index = incomplete_services_df.index + 1
            
            st.markdown(f"<h3>Klienci z usługami <span style='color: #ed3434; font-weight:700;font-size:30px'> DE - Niekompletny zestaw </span> ({len(incomplete_services_df)})</h3>", unsafe_allow_html=True)
            
            incomplete_services_styled = incomplete_services_df.style.apply(highlight_row_if_status, axis=1)
            st.dataframe(incomplete_services_styled)    
            
            #Klienci do wysłania

            if uninformed_or_unsent:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 1, 2, 6, 7, 5]  # Indeksy kolumn 1, 2, 3, 5, 7
                uninformed_or_unsent_filtered = [[row[i] for i in selected_columns] for row in uninformed_or_unsent]
                uninformed_or_unsent_df = pd.DataFrame(uninformed_or_unsent_filtered, columns=["Imię i Nazwisko", "Status", "Rok", "Poinformowany", "Wysłany", "UWAGI"])
            
            st.subheader(f"Klienci do wysłania (ilość: {len(uninformed_or_unsent_df)})")    
            uninformed_or_unsent_styled = uninformed_or_unsent_df.style.apply(highlight_status, axis=1)
            st.dataframe(uninformed_or_unsent_styled)
            
            #Klienci z zaliczką
            if downpayment_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 15,16, 17, 18, 19,5, 20]  # Indeksy kolumn 1, 2, 3, 5, 7
                downpayment_services_filtered = [[row[i] for i in selected_columns] for row in downpayment_services]
                downpayment_services_df = pd.DataFrame(downpayment_services_filtered, columns=["Imię i Nazwisko","Cena", "Status płatności", "Zapłacono", "Forma zapłaty", "Nr. faktury", "Uwagi","Data wystawienia faktury"])
            
            st.subheader(f"Klienci z zaliczką ({len(downpayment_services_df)})")
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