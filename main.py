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
import streamlit as st
import re
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
    # Zakodowanie zapisanego hasła na 'bytes'
    if isinstance(stored_password, str):
        stored_password = stored_password.encode('utf-8')

    # Porównanie hasła z jego haszem
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Autoryzacja do Google Sheets
SERVICE_ACCOUNT_INFO = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1k4UVgLa00Hqa7le3QPbwQMSXwpnYPlvcEQTxXqTEY4U'
SHEET_NAME_1 = 'ZP dane kont'
SHEET_NAME_2 = 'ZP status'

credentials = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, SCOPES)
client = gspread.authorize(credentials)
sheet1 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_1)
sheet2 = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME_2)

def fetch_clients():
    clients = []
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        clients.append(f"{row[1]} {row[0]} {row[3]}")
    return clients
def fetch_clients_biuro():
    """
    Pobiera dane klientów i zwraca słownik {pełne imię i nazwisko: biuro}.
    """
    clients_dict = {}  # Słownik do przechowywania klientów
    rows = sheet1.get_all_values()[1:]  # Pomijamy nagłówek

    for row in rows:
        if len(row) < 4:
            continue  # Pomijamy wiersze, które nie mają wystarczającej liczby kolumn
        
        full_name = f"{row[1]} {row[0]}" 
        biuro = row[2]  # Biuro klienta
        clients_dict[full_name] = biuro  # Dodajemy do słownika

    return clients_dict  # Zwracamy słownik
def client_exists(first_name, last_name, phone):
    rows = sheet1.get_all_values()[1:]  # Skip header row
    for row in rows:
        if row[0] == first_name and row[1] == last_name and row[3] == phone:
            return True
    return False

def add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office,steuernummer, tax_id, spouse_tax_id,Dataurodzenia,Religia,Ulica,Miejscowość,Dataslubu,DataUrŻony,imiezony,nazwisko_zony,UlicaMalzona,MiejscowoscMalzonka):
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
        Miejscowość,
        Dataslubu,
        DataUrŻony,
        imiezony,
        nazwisko_zony,
        UlicaMalzona,
        MiejscowoscMalzonka
    ]
    sheet1.append_row(new_row)
    st.success("Nowy klient został dodany")
def service_exists(klient, rok):
    rows = sheet2.get_all_values()[1:]  # Skip header row
    for row in rows:
        if row[0] == klient and row[2] == str(rok):
            return True
    return False
def add_service(klient,statusDE,rok,zwrot,opiekun,uwagi,poinformowany,wyslany,fahrkosten,ubernachtung,h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc,KlasaPITmałżonka,Bruttomałżonka,Podatekmałżonka,Dopłatamałżonka,Kościelnymałżonka,Kurzarbeitergeldmałżonka,Nr22malzonka,Nr23malzonka,Nr25malzonka,Nr26malzonka,Nr27malzonka,Pracodawcamalzonka,Chorobowemalzonka,Bezrobociepodatnika,Bezrobociemałżonka, delegacje_zagraniczne,rozliczycSamCzyRazem):
    if service_exists(klient, rok):
        st.markdown(f'<span style="border-radius:10px;padding:18px;background-color:rgba(255, 43, 43, 0.09);">Usługa dla klienta:<span style="font-size:18px; font-weight:bold;color:lightcoral"> {klient} </span>o statusie: <span style="font-size:18px; font-weight:bold;"> {statusDE}</span> za rok:<span style="font-size:18px; font-weight:bold;">  {rok}</span> już ISTNIEJE', unsafe_allow_html=True)
        return
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
        h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc,KlasaPITmałżonka,Bruttomałżonka,Podatekmałżonka,Dopłatamałżonka,Kościelnymałżonka,Kurzarbeitergeldmałżonka,Nr22malzonka,Nr23malzonka,Nr25malzonka,Nr26malzonka,Nr27malzonka,Pracodawcamalzonka,Chorobowemalzonka,Bezrobociepodatnika,Bezrobociemałżonka, delegacje_zagraniczne, rozliczycSamCzyRazem
    ]
    sheet2.append_row(new_row)
    st.success("Nowa usługa została dodana")


def edytuj_klienta():
    st.subheader("Edytuj klienta")

    # Fetch existing clients
    all_clients = fetch_clients()

    # Pole do filtrowania i wyboru klientów
    filtered_clients = [client for client in all_clients]

    klient = st.selectbox("Wybierz klienta do edycji", filtered_clients, key="selected_client")

    if len(klient)>2:
        st.subheader(f"Edycja klienta: {klient}")

        # Fetch client data based on the selected client
        client_data = None
        rows = sheet1.get_all_values()[1:]  # Skip header row
        for row in rows:
            if f"{row[1]} {row[0]} {row[3]}" == klient:
                client_data = row
                break

        if client_data:
            with st.form(key='info_form'):
                # Display and allow editing of client data
                first_name = st.text_input("Imię", client_data[0])
                last_name = st.text_input("Nazwisko", client_data[1])
                office = st.selectbox("Biuro", ["Przeworsk", "Jarosław"], index=["Przeworsk", "Jarosław"].index(client_data[2]))
                phone = st.text_input("Nr telefonu", client_data[3])
                email = st.text_input("Email", client_data[4])
                marital_status = st.selectbox('Stan cywilny', ['Kawaler', 'Żonaty', 'Rozwiedziony', 'Panienka', 'Mężatka'], index=['Kawaler', 'Żonaty', 'Rozwiedziony', 'Panienka', 'Mężatka'].index(client_data[5]))
                bank_account = st.text_input("Nr konta bankowego", client_data[6])
                swift = st.text_input("SWIFT", client_data[7])
                tax_office = st.text_input("Finanzamt", client_data[8])
                steuernummer = st.text_input("Steuernummer", client_data[9])
                tax_id = st.text_input("Nr ID", client_data[10])
                spouse_tax_id = st.text_input("Nr ID małżonka", client_data[11])
                Dataurodzenia = st.text_input("Data urodzenia", client_data[12])
                Religia = st.selectbox("Religia", ["", "VD", "RK", "EV"], index=["", "VD", "RK", "EV"].index(client_data[13]))
                Ulica = st.text_input("Ulica zamieszkania", client_data[14])
                Miejscowość = st.text_input("Kod pocztowy i miejscowość", client_data[15])
                Dataslubu = st.text_input("Data ślubu", client_data[16])
                DataUrŻony = st.text_input("Data urodzenia małżonka", client_data[17])
                imiezony = st.text_input("Imię małżonka", client_data[18])
                nazwisko_zony = st.text_input("Nazwisko małżonka (jeśli inne niż podatnikaa)", client_data[19])
                UlicaMalzona = st.text_input("Ulica zamieszkania małżonka (jeśli inne niż podatnikaa)", client_data[20])
                MiejscowoscMalzonka = st.text_input("Miejscowość zamieszkania małżonka (jeśli inne niż podatnikaa)", client_data[21])
                atualizuj_klienta = st.form_submit_button(label='Aktualizuj klienta')

            if atualizuj_klienta:
                all_clients = fetch_clients()
                updated_row = [
                    first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, steuernummer, tax_id, spouse_tax_id, Dataurodzenia, Religia, Ulica, Miejscowość, Dataslubu, DataUrŻony, imiezony,nazwisko_zony,UlicaMalzona,MiejscowoscMalzonka
                ]

                # Update the specific row in the Google Sheet
                cell_range = f'A{rows.index(client_data) + 2}:V{rows.index(client_data) + 2}'
                sheet1.update(cell_range, [updated_row])

                st.success("Dane klienta zostały zaktualizowane")
def edytuj_usluge():
    st.subheader("Edytuj usługę")

    all_clients = fetch_clients()
    all_services = fetch_services_data()

    # Dodajemy placeholder jako pierwszą opcję, aby domyślnie input był pusty
    service_options = ["Wybierz usługę"] + [f"{service_data[0]} - {service_data[2]}" for service_data in all_services]

    # Wyświetlamy selectbox; domyślnie pojawi się placeholder
    selected_service = st.selectbox("Wybierz usługę do edycji", service_options)

    # Jeżeli użytkownik wybierze usługę (inną niż placeholder), wyświetlamy resztę pól
    if selected_service != "Wybierz usługę":
        # Odejmujemy 1, bo pierwszy element to placeholder
        service_index = service_options.index(selected_service) - 1
        st.subheader(f"Edycja usługi: {selected_service}")
        service_data = all_services[service_index]
        
        with st.form(key="status_form"):
            poinformowany = st.selectbox("Poinformowany", ["Nie", "Tak"],
                                          index=["Nie", "Tak"].index(service_data[6]) if service_data[6] in ["Nie", "Tak"] else 0)
            wyslany = st.selectbox("Wysłane", ["Nie", "Tak"],
                                   index=["Nie", "Tak"].index(service_data[7]) if service_data[7] in ["Nie", "Tak"] else 0)

            klient = service_data[0]
            statusDE = st.selectbox(
                "Status DE", 
                ["", "DE - Niekompletny zestaw", "DE - Otrzymano dokumenty", "DE - Rozliczono"], 
                index=["", "DE - Niekompletny zestaw", "DE - Otrzymano dokumenty", "DE - Rozliczono"].index(service_data[1]) if service_data[1] in ["", "DE - Niekompletny zestaw", "DE - Otrzymano dokumenty", "DE - Rozliczono"] else 0
            )
            rozliczycSamCzyRazem = st.selectbox("Rozliczyć samego czy razem", ['Razem', 'Sam'],
                               index=['Razem', 'Sam'].index(service_data[70]) if service_data[70] in ['Razem', 'Sam'] else 'Razem') 
            rok = st.selectbox("Rok", ['2024','2023', '2022', '2021', '2020', '2019', '2018'],
                               index=['2024','2023', '2022', '2021', '2020', '2019', '2018'].index(service_data[2]) if service_data[2] in ['2024','2023', '2022', '2021', '2020', '2019', '2018'] else 0)
            zwrot = st.text_input("Zwrot", service_data[3])
            opiekun = st.selectbox("Opiekun", ["Kamil", "Beata", "Kasia"],
                                   index=["Kamil", "Beata", "Kasia"].index(service_data[4]) if service_data[4] in ["Kamil", "Beata", "Kasia"] else 0)
            uwagi = st.text_area("Uwagi", service_data[5])
           
            fahrkosten = st.text_input("Fahrkosten", service_data[8]) 
            ubernachtung = st.text_input("Übernachtung", service_data[9]) 
            h24 = st.text_input("24h", service_data[10]) 
            h8 = st.text_input("8h", service_data[11]) 
            wKabinie = st.text_input("Kabine", service_data[12]) 
            anUndAb = st.text_input("Ab und an", service_data[13]) 
            dzieci = st.text_area("Dzieci", service_data[14])            
                   
            
            zarobkiMezaEuro = service_data[21]
            zarobZonyEuro = service_data[22]
            cena = st.selectbox("Cena", ["", "250", "450", "400", "300", "200"],
                                  index=["", "250", "450", "400", "300", "200"].index(service_data[15]) if service_data[15] in ["", "250", "450", "400", "300", "200"] else 0) 
            statusPlatnosciu = st.selectbox("Status", ["Nieopłacony", "Zaliczka", "Opłacony"],
                                            index=["Nieopłacony", "Zaliczka", "Opłacony"].index(service_data[16]) if service_data[16] in ["Nieopłacony", "Zaliczka", "Opłacony"] else 0) 
            zaplacono = st.text_input("Zapłacono", service_data[17])
            formaZaplaty = st.selectbox("Metoda płatności", ["", "Przelew", "Gotowka", "Faktura"],
                                        index=["", "Przelew", "Gotowka", "Faktura"].index(service_data[18]) if service_data[18] in ["", "Przelew", "Gotowka", "Faktura"] else 0) 
            nrfaktury = st.text_input("Nr. Faktury", service_data[19])
            dataWystawieniaFaktury = st.text_input("Data wystawienia faktury", service_data[20])
            
            nr22 = service_data[23]
            nr23 = service_data[24]
            nr25 = service_data[25]
            nr26 = service_data[26]
            nr27 = service_data[27]
            pracodawca = service_data[28]
            chorobowe = service_data[29]

            klasaPIT1 = service_data[30]
            brutto1 = service_data[31]
            podatek1 = service_data[32]
            dopłata1 = service_data[33]
            kościelny1 = service_data[34]
            kurzarbeitergeld1 = service_data[35]
            
            klasaPIT2 = service_data[36]
            brutto2 = service_data[37]
            podatek2 = service_data[38]
            dopłata2 = service_data[39]
            kościelny2 = service_data[40]
            kurzarbeitergeld2 = service_data[41]

            klasaPIT3 = service_data[42]
            brutto3 = service_data[43]
            podatek3 = service_data[44]
            dopłata3 = service_data[45]
            kościelny3 = service_data[46]
            kurzarbeitergeld3 = service_data[47]
            
            kontoElster = st.selectbox("Czy podatnik ma konto ELSTER", ["Nie", "Tak"],
                                         index=["Nie", "Tak"].index(service_data[48]) if service_data[48] in ["Nie", "Tak"] else 0) 
            ogrObPodatkowy = st.selectbox("Ograniczony obowiązek podatkowy", ["Nie", "Tak"],
                                          index=["Nie", "Tak"].index(service_data[49]) if service_data[49] in ["Nie", "Tak"] else 0)            
            aktualny_stan_zamieszkania = st.text_input("Aktualny kraj zamieszkania", service_data[50])
            miejsce_urodzenia = st.text_input("Miejscowość urodzenia", service_data[51]) 
            kraj_urodzenia = st.text_input("Kraj urodzenia", service_data[52])
            narodowosc = st.text_input("Narodowość", service_data[53]) 
            
            KlasaPITmałżonka = service_data[54]
            Bruttomałżonka = service_data[55]
            Podatekmałżonka = service_data[56]
            Dopłatamałżonka = service_data[57]
            Kościelnymałżonka = service_data[58]
            Kurzarbeitergeldmałżonka = service_data[59]
            
            Nr22malzonka = service_data[60]
            Nr23malzonka = service_data[61]
            Nr25malzonka = service_data[62]
            Nr26malzonka = service_data[63]
            Nr27malzonka = service_data[64]
            Pracodawcamalzonka = service_data[65]
            Chorobowemalzonka = st.text_input("Chorobowemalzonka", service_data[66])
            Bezrobociepodatnika = st.text_input("Bezrobocie podatnika", service_data[67]) 
            Bezrobociemałżonka = st.text_input("Bezrobocie małżonka", service_data[68])
            
            delegacje_zagraniczne = st.text_input("Delegacje zagraniczne", service_data[69]) 
            aktualizuj_usluge = st.form_submit_button(label='Aktualizuj usługę')

        if aktualizuj_usluge:
            updated_row = [
                klient, statusDE, rok, zwrot, opiekun, uwagi, poinformowany, wyslany,
                fahrkosten, ubernachtung, h24, h8, wKabinie, anUndAb, dzieci,
                cena, statusPlatnosciu, zaplacono, formaZaplaty, nrfaktury, dataWystawieniaFaktury,
                zarobkiMezaEuro, zarobZonyEuro, nr22, nr23, nr25, nr26, nr27,
                pracodawca, chorobowe, klasaPIT1, brutto1, podatek1, dopłata1, kościelny1, kurzarbeitergeld1,
                klasaPIT2, brutto2, podatek2, dopłata2, kościelny2, kurzarbeitergeld2,
                klasaPIT3, brutto3, podatek3, dopłata3, kościelny3, kurzarbeitergeld3,
                kontoElster, ogrObPodatkowy, aktualny_stan_zamieszkania, miejsce_urodzenia,
                kraj_urodzenia, narodowosc, KlasaPITmałżonka, Bruttomałżonka, Podatekmałżonka,
                Dopłatamałżonka, Kościelnymałżonka, Kurzarbeitergeldmałżonka, Nr22malzonka,
                Nr23malzonka, Nr25malzonka, Nr26malzonka, Nr27malzonka, Pracodawcamalzonka,
                Chorobowemalzonka, Bezrobociepodatnika, Bezrobociemałżonka, delegacje_zagraniczne,rozliczycSamCzyRazem
            ]

            # Definiujemy zakres, aby pokryć wszystkie kolumny z updated_row
            cell_range = f'A{service_index + 2}:BS{service_index + 2}'

            # Aktualizujemy konkretny wiersz w Google Sheet
            sheet2.update(cell_range, [updated_row])

            st.success("Dane usługi zostały zaktualizowane")

def fetch_services_data():
    rows = sheet2.get_all_values()[1:]  # Skip header row
    return rows
def extract_name(full_string):
    """
    Funkcja wyodrębnia tylko nazwisko i imię z ciągu tekstowego.
    Pomija numer telefonu i ewentualne dane w nawiasach.
    """
    match = re.match(r"([A-ZŻŹĆĄŚĘŁÓŃ]+) ([A-ZŻŹĆĄŚĘŁÓŃ]+)", full_string)
    if match:
        return f"{match.group(1)} {match.group(2)}"  # Nazwisko + Imię
    return full_string  # Jeśli nie pasuje, zwróć oryginał
def edytuj_usluge_skrocona():
    # Jeśli poprzednia aktualizacja zakończyła się powodzeniem, wyświetl komunikat
    if st.session_state.get("update_success", False):
        st.success("Dane usługi zostały zaktualizowane")
        del st.session_state["update_success"]

    st.subheader("Edytuj usługę - Kamil")

    all_clients = fetch_clients()
    all_services = fetch_services_data()

    # Dodajemy placeholder jako pierwszą opcję, aby domyślnie input był pusty
    service_options = ["Wybierz usługę"] + [f"{service_data[0]} - {service_data[2]}" for service_data in all_services]

    # Wyświetlamy selectbox; domyślnie pojawi się placeholder
    selected_service = st.selectbox("Wybierz usługę do edycji", service_options)

    # Jeżeli użytkownik wybierze usługę (inną niż placeholder), wyświetlamy resztę pól
    if selected_service != "Wybierz usługę":
        # Odejmujemy 1, bo pierwszy element to placeholder
        service_index = service_options.index(selected_service) - 1
        st.subheader(f"Edycja usługi: {selected_service}")
        service_data = all_services[service_index]
        
        with st.form(key="status_form2"):
            CzyJestPitMałżonka = st.checkbox("Pit małżonka (kiedy rozliczają się razem)", key="CzyJestPitMałżonka")
            pola_ogr_ob_podat = st.checkbox("Ograniczony obowiązek podatkowy", key="pola_ogr_ob_podat")
            Bezrobocie = st.checkbox("BEZROBOCIE", key="Bezrobocie")
            delegacje = st.checkbox("Delegacje zagraniczne", key="delegacje")
            edytujPlatnosc = st.checkbox("Płatności (cena, status platnosci, faktura, zaplacono)", key="edytujPlatnosc")
            # Wyświetlenie aktualnych wartości pól
            st.markdown("**Aktualne wartości:**")
            st.text(f"Konto ELSTER: {service_data[48]}")
            st.text(f"Ograniczony obowiązek podatkowy: {service_data[49]}")
            st.text(f"Rok: {service_data[2]}")
            st.text(f"Opiekun: {service_data[4]}")
            aktualneWartosci = st.checkbox("Edytuj Aktualne Wartości", key="akwart")

            st.form_submit_button(label='Załaduj')

        with st.form(key="status_form"):
            klient = service_data[0] 
            statusDE = service_data[1]
            rok = st.selectbox("Rok", ['2024','2023', '2022', '2021', '2020', '2019', '2018'],
                               index=['2024','2023', '2022', '2021', '2020', '2019', '2018'].index(service_data[2]) if service_data[2] in ['2024','2023', '2022', '2021', '2020', '2019', '2018'] else 0) if aktualneWartosci else service_data[2]
            zwrot = service_data[3]
            opiekun = st.selectbox("Opiekun", ["Kamil", "Beata", "Kasia"],
                                   index=["Kamil", "Beata", "Kasia"].index(service_data[4]) if service_data[4] in ["Kamil", "Beata", "Kasia"] else 0) if aktualneWartosci else service_data[4]
            kontoElster = st.selectbox("Czy podatnik ma konto ELSTER", ["Nie", "Tak"],
                                         index=["Nie", "Tak"].index(service_data[48]) if service_data[48] in ["Nie", "Tak"] else 0) if aktualneWartosci else service_data[48]
            ogrObPodatkowy = st.selectbox("Ograniczony obowiązek podatkowy", ["Nie", "Tak"],
                                          index=["Nie", "Tak"].index(service_data[49]) if service_data[49] in ["Nie", "Tak"] else 0) if aktualneWartosci else service_data[49]     
            uwagi = st.text_area("Uwagi", service_data[5])
            poinformowany = service_data[6]
            wyslany = service_data[7]

            fahrkosten = st.text_input("Fahrkosten", service_data[8]) 
            ubernachtung = st.text_input("Übernachtung", service_data[9]) 
            h24 = st.text_input("24h", service_data[10]) 
            h8 = st.text_input("8h", service_data[11]) 
            wKabinie = st.text_input("Kabine", service_data[12]) 
            anUndAb = st.text_input("Ab und an", service_data[13]) 
            dzieci = st.text_area("Dzieci", service_data[14])            
            
            zarobkiMezaEuro = st.text_input("Zarobki podatnika", service_data[21])
            zarobZonyEuro = st.text_input("Zarobi małżonka", service_data[22])
            cena = st.selectbox("Cena", ["", "250", "450", "400", "300", "200"],
                                  index=["", "250", "450", "400", "300", "200"].index(service_data[15]) if service_data[15] in ["", "250", "450", "400", "300", "200"] else 0) if edytujPlatnosc else service_data[15]
            statusPlatnosciu = st.selectbox("Status", ["Nieopłacony", "Zaliczka", "Opłacony"],
                                            index=["Nieopłacony", "Zaliczka", "Opłacony"].index(service_data[16]) if service_data[16] in ["Nieopłacony", "Zaliczka", "Opłacony"] else 0) if edytujPlatnosc else service_data[16]
            zaplacono = st.text_input("Zapłacono", service_data[17]) if edytujPlatnosc else service_data[17]
            formaZaplaty = st.selectbox("Metoda płatności", ["", "Przelew", "Gotowka", "Faktura"],
                                        index=["", "Przelew", "Gotowka", "Faktura"].index(service_data[18]) if service_data[18] in ["", "Przelew", "Gotowka", "Faktura"] else 0) if edytujPlatnosc else service_data[18]
            nrfaktury = st.text_input("Nr. Faktury", service_data[19]) if edytujPlatnosc else service_data[19]
            dataWystawieniaFaktury = st.text_input("Data wystawienia faktury", service_data[20]) if edytujPlatnosc else service_data[20]
            
            nr22 = st.text_input("nr22", service_data[23]) 
            nr23 = st.text_input("nr23", service_data[24]) 
            nr25 = st.text_input("nr25", service_data[25]) 
            nr26 = st.text_input("nr26", service_data[26]) 
            nr27 = st.text_input("nr27", service_data[27]) 
            pracodawca = st.text_input("pracodawca", service_data[28]) 
            chorobowe = st.text_input("chorobowe", service_data[29]) 

            klasaPIT1 = st.text_input("klasaPIT1", service_data[30]) 
            brutto1 = st.text_input("brutto1", service_data[31]) 
            podatek1 = st.text_input("podatek1", service_data[32]) 
            dopłata1 = st.text_input("dopłata1", service_data[33]) 
            kościelny1 = st.text_input("kościelny1", service_data[34]) 
            kurzarbeitergeld1 = st.text_input("kurzarbeitergeld1", service_data[35]) 
            
            klasaPIT2 = st.text_input("klasaPIT2", service_data[36]) 
            brutto2 = st.text_input("brutto2", service_data[37]) 
            podatek2 = st.text_input("podatek2", service_data[38]) 
            dopłata2 = st.text_input("dopłata2", service_data[39]) 
            kościelny2 = st.text_input("kościelny2", service_data[40]) 
            kurzarbeitergeld2 = st.text_input("kurzarbeitergeld2", service_data[41]) 

            klasaPIT3 = st.text_input("klasaPIT3", service_data[42]) 
            brutto3 = st.text_input("brutto3", service_data[43]) 
            podatek3 = st.text_input("podatek3", service_data[44]) 
            dopłata3 = st.text_input("dopłata3", service_data[45]) 
            kościelny3 = st.text_input("kościelny3", service_data[46]) 
            kurzarbeitergeld3 = st.text_input("kurzarbeitergeld3", service_data[47]) 
            
    
            aktualny_stan_zamieszkania = st.text_input("Aktualny kraj zamieszkania", service_data[50]) if pola_ogr_ob_podat else service_data[50]
            miejsce_urodzenia = st.text_input("Miejscowość urodzenia", service_data[51]) if pola_ogr_ob_podat else service_data[51]
            kraj_urodzenia = st.text_input("Kraj urodzenia", service_data[52]) if pola_ogr_ob_podat else service_data[52]
            narodowosc = st.text_input("Narodowość", service_data[53]) if pola_ogr_ob_podat else service_data[53]
            
            KlasaPITmałżonka = st.text_input("KlasaPITmałżonka", service_data[54]) if CzyJestPitMałżonka else service_data[54]
            Bruttomałżonka = st.text_input("Bruttomałżonka", service_data[55]) if CzyJestPitMałżonka else service_data[55]
            Podatekmałżonka = st.text_input("Podatekmałżonka", service_data[56]) if CzyJestPitMałżonka else service_data[56]
            Dopłatamałżonka = st.text_input("Dopłatamałżonka", service_data[57]) if CzyJestPitMałżonka else service_data[57]
            Kościelnymałżonka = st.text_input("Kościelnymałżonka", service_data[58]) if CzyJestPitMałżonka else service_data[58]
            Kurzarbeitergeldmałżonka = st.text_input("Kurzarbeitergeldmałżonka", service_data[59]) if CzyJestPitMałżonka else service_data[59]
            
            Nr22malzonka = st.text_input("Nr22malzonka", service_data[60]) if CzyJestPitMałżonka else service_data[60]
            Nr23malzonka = st.text_input("Nr23malzonka", service_data[61]) if CzyJestPitMałżonka else service_data[61]
            Nr25malzonka = st.text_input("Nr25malzonka", service_data[62]) if CzyJestPitMałżonka else service_data[62]
            Nr26malzonka = st.text_input("Nr26malzonka", service_data[63]) if CzyJestPitMałżonka else service_data[63]
            Nr27malzonka = st.text_input("Nr27malzonka", service_data[64]) if CzyJestPitMałżonka else service_data[64]
            Pracodawcamalzonka = st.text_input("Pracodawcamalzonka", service_data[65]) if CzyJestPitMałżonka else service_data[65]
            Chorobowemalzonka = st.text_input("Chorobowemalzonka", service_data[66]) if CzyJestPitMałżonka else service_data[66]
            Bezrobociepodatnika = st.text_input("Bezrobocie podatnika", service_data[67]) if Bezrobocie else service_data[67]
            Bezrobociemałżonka = st.text_input("Bezrobocie małżonka", service_data[68]) if Bezrobocie else service_data[68]
            
            delegacje_zagraniczne = st.text_input("Delegacje zagraniczne", service_data[69]) if delegacje else service_data[69]

            
            aktualizuj_usluge = st.form_submit_button(label='Aktualizuj usługę')

        if aktualizuj_usluge:
            updated_row = [
                klient, statusDE, rok, zwrot, opiekun, uwagi, poinformowany, wyslany,
                fahrkosten, ubernachtung, h24, h8, wKabinie, anUndAb, dzieci,
                cena, statusPlatnosciu, zaplacono, formaZaplaty, nrfaktury, dataWystawieniaFaktury,
                zarobkiMezaEuro, zarobZonyEuro, nr22, nr23, nr25, nr26, nr27,
                pracodawca, chorobowe, klasaPIT1, brutto1, podatek1, dopłata1, kościelny1, kurzarbeitergeld1,
                klasaPIT2, brutto2, podatek2, dopłata2, kościelny2, kurzarbeitergeld2,
                klasaPIT3, brutto3, podatek3, dopłata3, kościelny3, kurzarbeitergeld3,
                kontoElster, ogrObPodatkowy, aktualny_stan_zamieszkania, miejsce_urodzenia,
                kraj_urodzenia, narodowosc, KlasaPITmałżonka, Bruttomałżonka, Podatekmałżonka,
                Dopłatamałżonka, Kościelnymałżonka, Kurzarbeitergeldmałżonka, Nr22malzonka,
                Nr23malzonka, Nr25malzonka, Nr26malzonka, Nr27malzonka, Pracodawcamalzonka,
                Chorobowemalzonka, Bezrobociepodatnika, Bezrobociemałżonka, delegacje_zagraniczne
            ]

            cell_range = f'A{service_index + 2}:BS{service_index + 2}'
            sheet2.update(cell_range, [updated_row])
            st.session_state["update_success"] = True
            st.rerun()


def fetch_full_status_data():
    rows = sheet2.get_all_values()  # Include header row
    return pd.DataFrame(rows[1:], columns=rows[0])

def update_status_data(df):
    sheet2.clear()
    sheet2.append_row(df.columns.tolist())
    for row in df.values.tolist():
        sheet2.append_row(row)

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
        styles[4] = 'background-color: red; color: white;'
    if row['Wysłany'] == "Nie":
        styles[5] = 'background-color: red; color: white;'
    if row['Poinformowany'] == "Tak":
        styles[4] = 'background-color: green; color: white;'
    if row['Wysłany'] == "Tak":
        styles[5] = 'background-color: green; color: white;'
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
    hashed_passwords = load_hashed_passwords()
    usernames = ["kkamil", "bbeata", "kkasia"]  # Lista nazw użytkowników

    if "logged_in" not in cookies:
        cookies["logged_in"] = "False"

    # Logowanie
    if cookies.get("logged_in") != "True":
        st.sidebar.title("Logowanie")
        username = st.sidebar.text_input("Nazwa użytkownika")
        password = st.sidebar.text_input("Hasło", type="password")

        if st.sidebar.button("Zaloguj się"):
            if username in usernames:
                user_index = usernames.index(username)
                if verify_password(hashed_passwords[user_index], password):
                    st.sidebar.success("Zalogowano pomyślnie")
                    cookies["logged_in"] = "True"
                    cookies["username"] = username
                    cookies.save()
                    st.experimental_rerun()  # Przeładuj stronę po zalogowaniu
                else:
                    st.sidebar.error("Błędne hasło")
            else:
                st.sidebar.error("Błędna nazwa użytkownika")
    else:
        # Menu na górze strony po zalogowaniu
        menu = ["Podsumowanie", "Dodaj klienta", "Dodaj usługę", "Cały excel", "Edytuj klienta", "Edytuj usługę", "Edytuj usługę - Kamil"]
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
            st.session_state["Miejscowość"] = ""
            st.session_state["marital_status"] = ""
            st.session_state["Dataslubu"] = ""
            st.session_state["imiezony"] = ""
            st.session_state["spouse_tax_id"] = ""
            st.session_state["DataUrŻony"] = ""
            st.session_state["nazwisko_zony"] = ""
            st.session_state["UlicaMalzona"] = ""
            st.session_state["MiejscowoscMalzonka"] = ""
        
        # Sekcja dodawania klienta
        if choice == "Dodaj klienta":
            st.subheader("Dodaj nowego klienta")

            # Przycisk do czyszczenia formularza
            if st.button("Wyczyść"):
                reset_client_form()

            # Ustawienie początkowego stanu
            
            marital_status2 = st.selectbox('Stan cywilny:', ['Kawaler', 'Żonaty', 'Rozwiedziony', 'Panienka', 'Mężatka'])
            st.session_state["marital_status"] = marital_status2
             

            with st.form(key="client_info_form", border=False):
                office = st.selectbox("Biuro", ["Przeworsk", "Jarosław"], key="office")
                first_name = st.text_input("Imię", key="first_name")
                first_name = first_name.upper()if first_name else None
                last_name = st.text_input("Nazwisko", key="last_name")
                last_name = last_name.upper() if last_name else None
                phone = st.text_input("Nr telefonu", key="phone")
                email = st.text_input("Email", key="email")
                bank_account = st.text_input("Nr konta bank", key="bank_account")
                bank_account = bank_account.upper() if bank_account else None
                swift = st.text_input("SWIFT", key="swift")
                swift = swift.upper() if swift else None
                tax_office = st.text_input("Finanzamt", key="tax_office")
                tax_office = tax_office.upper() if tax_office else None
                steuernummer = st.text_input("Steuernummer", key="steuernummer")
                tax_id = st.text_input("Nr ID", key="tax_id")
                if marital_status2 == "Żonaty" or marital_status2 == "Mężatka":
                    spouse_tax_id = st.text_input("Nr ID małżonka", key="spouse_tax_id")
                Dataurodzenia = st.text_input("Data urodzenia podatnika", key="Dataurodzenia")
                if marital_status2 == "Żonaty" or marital_status2 == "Mężatka":
                    DataUrŻony = st.text_input("Data urodzenia małżonka", key="DataUrŻony")
                Religia = st.selectbox("Religia", ["", "VD", "RK", "EV"], key="Religia")
                Ulica = st.text_input("Ulica zamieszkania podatnika", key="Ulica")
                Ulica = Ulica.upper() if Ulica else None
                Miejscowość = st.text_input("Kod pocztowy i miejscowość", key="Miejscowość")  
                Miejscowość = Miejscowość.upper() if Miejscowość else None

                marital_status = st.text_input("Stan cywilny", key="marital_status",disabled=True)
                if marital_status2 == "Żonaty" or marital_status2 == "Mężatka":
                    st.session_state["marital_status2"] = "Żonaty"
                    Dataslubu = st.text_input("Data ślubu", key="Dataslubu")
                    imiezony = st.text_input("Imię małżonka", key="imiezony")
                    imiezony = imiezony.upper() if imiezony else None
                    nazwisko_zony = st.text_input("Nazwisko małżonka (jeśli inne niż podatnika)", key="nazwisko_zony")
                    UlicaMalzona = st.text_input("Ulica zamieszkania małżonka (jeśli inne niż podatnika)", key="UlicaMalzona")
                    MiejscowoscMalzonka = st.text_input("Miejscowość zamieszkania małżonka (jeśli inne niż podatnika)", key="MiejscowoscMalzonka")

                else:
                    Dataslubu = ""
                    imiezony = ""
                    spouse_tax_id = ""
                    DataUrŻony = ""
                    nazwisko_zony = ""
                    UlicaMalzona = ""
                    MiejscowoscMalzonka = ""
                submit_info = st.form_submit_button(label='Dodaj klienta')


            if submit_info:
                add_client(first_name, last_name, office, phone, email, marital_status, bank_account, swift, tax_office, steuernummer, tax_id, spouse_tax_id, Dataurodzenia, Religia, Ulica, Miejscowość, Dataslubu, DataUrŻony, imiezony,nazwisko_zony,UlicaMalzona,MiejscowoscMalzonka)

        # Funkcja do resetowania formularza dodawania usługi
        def reset_service_form():
            st.session_state["klient"] = "  "
            st.session_state["statusDE"] = ""
            st.session_state["rok"] = "2024"
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
            st.session_state["KlasaPITmałżonka"] = ""
            st.session_state["Bruttomałżonka"] = ""
            st.session_state["Podatekmałżonka"] = ""
            st.session_state["Dopłatamałżonka"] = ""
            st.session_state["Kościelnymałżonka"] = ""
            st.session_state["Kurzarbeitergeldmałżonka"] = ""
            st.session_state["Nr22malzonka"] = ""
            st.session_state["Nr23malzonka"] = ""
            st.session_state["Nr25malzonka"] = ""
            st.session_state["Nr26malzonka"] = ""
            st.session_state["Nr27malzonka"] = ""
            st.session_state["Pracodawcamalzonka"] = ""
            st.session_state["Chorobowemalzonka"] = ""
            st.session_state["Bezrobociepodatnika"] = ""
            st.session_state["Bezrobociemałżonka"] = ""
        if choice == "Dodaj usługę":
            st.subheader("Dodaj nową usługę")

            # Przycisk do czyszczenia formularza
            if st.button("Wyczyść wszystkie pola"):
                reset_service_form()
            all_clients = fetch_clients()
            st.subheader("Zaznacz odpowiednie opcje")

            kamil = st.checkbox("Zaznaczyć aby wyświetlić pola rozszerzone (KAMIL) ", key="kamil")

            with st.form(key="pola_form"):

                ogrObPodatkowy2 = st.selectbox("Ograniczony obowiązek podatkowy", ["Nie", "Tak"], key="ogrObPodatkowy2")
                if kamil:
                    zarobkiwPolsce = st.checkbox("Zaznacz, aby dodać zarobki w Polsce", key="zarobkiwPolsce")
                    dodatkowe = st.checkbox("Zaznacz, aby dodać pola 22, 23, 25, 26, 27, pracodawca, chorobowe", key="dodatkowe")
                    CzyJestPit1 = st.checkbox("PIT nr. 1 (Zaznaczyć, jeżeli klient posiada) ", key="CzyJestPit1") 
                    CzyJestPit2 = st.checkbox("PIT nr. 2 (Zaznaczyć, jeżeli klient posiada)", key="CzyJestPit2")
                    CzyJestPit3 = st.checkbox("PIT nr. 3 (Zaznaczyć, jeżeli klient posiada)", key="CzyJestPit3")
                    CzyJestPitMałżonka = st.checkbox("PIT małżonka (Zaznaczyć, jeżeli istnieje)", key="CzyJestPitMałżonka")
                else:
                    zarobkiwPolsce = ""
                    dodatkowe = ""
                    CzyJestPit1 = ""
                    CzyJestPit2 = ""
                    CzyJestPit3 = ""
                    CzyJestPitMałżonka = ""
                formaZaplaty2 = st.selectbox("Metoda płatności", ["", "Przelew", "Gotowka", "Faktura"], key="formaZaplaty2")
                bezrobocie = st.checkbox("Czy sa dokumenty BEZROBOCIE", key="bezrobocie")
                delegacje = st.checkbox("Czy są delegacje zagraniczne", key="delegacje")
                num_delegacje = st.number_input("Ile krajów? (delegacje zagraniczne)", min_value=1, max_value=10, step=1, key="num_delegacje")

                st.form_submit_button(label='Załaduj pola')
            
        
            st.session_state["ogrObPodatkowy"] = ogrObPodatkowy2
            st.session_state["formaZaplaty"] = formaZaplaty2
            
            st.subheader("Wypełnij dane usługi")
            with st.form(key="status_form", border=False):
                klient = st.selectbox("Podatnik", all_clients, key="klient2")
                rozliczycSamCzyRazem = st.selectbox("Rozliczyć samego czy razem?", ['Razem','Sam'], key="rozliczycSamCzyRazem")
                statusDE = st.selectbox("Status DE", ["", "DE - Niekompletny zestaw", "DE - Otrzymano dokumenty", "DE - Rozliczono"], key="statusDE")
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
                chorobowe = st.text_input("Chorobowe", key="chorobowe")
                pracodawca = st.text_input("pracodawca", key="pracodawca")
                cena = st.selectbox("Cena", ["", "250", "450", "400", "300","200"], key="cena")
                statusPlatnosciu = st.selectbox("Status", ["Nieopłacony", "Zaliczka", "Opłacony"], key="statusPlatnosciu")
                zaplacono = st.text_input("Zapłacono", key="zaplacono")
                zwrot = ""
                formaZaplaty = st.text_input("Metoda płatności", key="formaZaplaty", disabled=True)
                if formaZaplaty == "Faktura":
                    nrfaktury = st.text_input("Nr. Faktury", key="nrfaktury")
                    dataWystawieniaFaktury = st.text_input("Data wystawienia faktury", key="dataWystawieniaFaktury")                
                else:
                    nrfaktury = ""
                    dataWystawieniaFaktury = ""
                kontoElster = st.selectbox("Czy podatnik ma konto ELSTER", ["Nie", "Tak"], key="kontoElster")                  
                ogrObPodatkowy = st.selectbox("Ograniczony obowiązek podatkowy", ["Nie", "Tak"], key="ogrObPodatkowy",disabled=True)
                
                if ogrObPodatkowy == "Tak":
                    aktualny_stan_zamieszkania = st.text_input("Aktualny kraj zamieszkania", key="aktualny_stan_zamieszkania")
                    miejsce_urodzenia = st.text_input("Miejscowość urodzenia", key="miejsce_urodzenia")
                    kraj_urodzenia = st.text_input("Kraj urodzenia", key="kraj_urodzenia")
                    narodowosc = st.text_input("Narodowość", key="narodowosc")                 
                else:
                    aktualny_stan_zamieszkania = ""
                    miejsce_urodzenia = ""
                    kraj_urodzenia = ""
                    narodowosc = ""

                if zarobkiwPolsce:
                    zarobkiMezaEuro = st.text_input("Zarobki podatnika", key="zarobkiMezaEuro")
                    zarobZonyEuro = st.text_input("Zarobki małżonka", key="zarobZonyEuro")            
                else:
                    zarobkiMezaEuro = ""
                    zarobZonyEuro = ""

                if dodatkowe:
                    nr22 = st.text_input("nr22", key="nr22")
                    nr23 = st.text_input("nr23", key="nr23")
                    nr25 = st.text_input("nr25", key="nr25")
                    nr26 = st.text_input("nr26", key="nr26")
                    nr27 = st.text_input("nr27", key="nr27")
                else:
                    nr22 = ""
                    nr23 = ""
                    nr25 = ""
                    nr26 = ""
                    nr27 = ""

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
                
                if CzyJestPitMałżonka:   
                    KlasaPITmałżonka = st.text_input("KlasaPITmałżonka", key="KlasaPITmałżonka")
                    Bruttomałżonka = st.text_input("Bruttomałżonka", key="Bruttomałżonka")
                    Podatekmałżonka = st.text_input("Podatekmałżonka", key="Podatekmałżonka")
                    Dopłatamałżonka = st.text_input("Dopłatamałżonka", key="Dopłatamałżonka")
                    Kościelnymałżonka = st.text_input("Kościelnymałżonka", key="Kościelnymałżonka")
                    Kurzarbeitergeldmałżonka = st.text_input("Kurzarbeitergeldmałżonka", key="Kurzarbeitergeldmałżonka")
                    Nr22malzonka = st.text_input("Nr22 malzonka", key="Nr22malzonka")
                    Nr23malzonka = st.text_input("Nr23 malzonka", key="Nr23malzonka")
                    Nr25malzonka = st.text_input("Nr25 malzonka", key="Nr25malzonka")
                    Nr26malzonka = st.text_input("Nr26 malzonka", key="Nr26malzonka")
                    Nr27malzonka = st.text_input("Nr27 malzonka", key="Nr27malzonka")
                    Pracodawcamalzonka = st.text_input("Pracodawca malzonka", key="Pracodawcamalzonka")
                    Chorobowemalzonka = st.text_input("Chorobowe malzonka", key="Chorobowemalzonka")
                else:
                    Nr22malzonka = ""
                    Nr23malzonka = ""
                    Nr25malzonka = ""
                    Nr26malzonka = ""
                    Nr27malzonka = ""
                    Pracodawcamalzonka = ""
                    Chorobowemalzonka = ""
                    KlasaPITmałżonka = ""
                    Bruttomałżonka = ""
                    Podatekmałżonka = ""
                    Dopłatamałżonka = ""
                    Kościelnymałżonka = ""
                    Kurzarbeitergeldmałżonka = ""
                if bezrobocie:
                    Bezrobociepodatnika = st.text_input("Bezrobociepodatnika", key="Bezrobociepodatnika")
                    Bezrobociemałżonka = st.text_input("Bezrobocie małżonka", key="Bezrobociemałżonka")
                else:
                    Bezrobociepodatnika = ""
                    Bezrobociemałżonka = ""
                
                delegacje_zagraniczne = []
                if delegacje:
                    st.write("Dodaj kraje i ilość dni delegacji")
                    kraje = ["","DEUTSCHLAND", "BELGIEN", "FRANKREICH", "SCHWEDEN","DÄNEMARK","NIEDERLANDE","ENGLAND",'TSCHECHEIN','ITALIEN','ÖSTERREICH','POLEN','LUXEMBURG','UNGARN','SCHWEIZ']

                    for i in range(num_delegacje):
                        st.write(f"Delegacja {i+1}")
                        col1, col2 = st.columns(2)
                        with col1:
                            kraj = st.selectbox(f"Kraj {i+1}", kraje, key=f"kraj_{i}")
                        with col2:
                            ilosc_dni_delegacji = st.number_input(f"Ilość dni {i+1}", min_value=1, key=f"ilosc_dni_{i}")
                        delegacje_zagraniczne.append((kraj, ilosc_dni_delegacji))
            
                submit_status = st.form_submit_button(label='Dodaj usługę')

            if submit_status:
                if not klient or not statusDE or not rok:
                    st.error("Podanie danych klienta, Statusu DE oraz roku rozliczenia jest wymagane")
                else:
                    delegacje_str = ";".join([f"{kraj} {dni}" for kraj, dni in delegacje_zagraniczne])
                    add_service(klient,statusDE,rok,zwrot,opiekun,uwagi,poinformowany,wyslany,fahrkosten,ubernachtung,h24,h8,wKabinie,anUndAb,dzieci,cena,statusPlatnosciu,zaplacono,formaZaplaty,nrfaktury,dataWystawieniaFaktury,zarobkiMezaEuro,zarobZonyEuro,nr22,nr23,nr25,nr26,nr27,pracodawca,chorobowe,klasaPIT1,brutto1,podatek1,dopłata1,kościelny1,kurzarbeitergeld1,klasaPIT2,brutto2,podatek2,dopłata2,kościelny2,kurzarbeitergeld2,klasaPIT3,brutto3,podatek3,dopłata3,kościelny3,kurzarbeitergeld3,kontoElster,ogrObPodatkowy,aktualny_stan_zamieszkania,miejsce_urodzenia,kraj_urodzenia,narodowosc,KlasaPITmałżonka,Bruttomałżonka,Podatekmałżonka,Dopłatamałżonka,Kościelnymałżonka,Kurzarbeitergeldmałżonka,Nr22malzonka,Nr23malzonka,Nr25malzonka,Nr26malzonka,Nr27malzonka,Pracodawcamalzonka,Chorobowemalzonka,Bezrobociepodatnika,Bezrobociemałżonka,delegacje_str,rozliczycSamCzyRazem)       
        elif choice == "Podsumowanie":
            st.subheader("Podsumowanie")

            # Pobieranie danych
            total_clients = len(sheet1.get_all_values()) - 1  # Pomijamy nagłówek
            clients_dict = fetch_clients_biuro()  # Słownik { "Imię Nazwisko": "Biuro" }
            services_data = fetch_services_data()
            total_services = len(services_data)

            # Filtracja danych
            incomplete_services = [s for s in services_data if s[1] == "DE - Niekompletny zestaw"]
            processed_services = [s for s in services_data if s[1] == "DE - Rozliczono"]
            received_docs_services = [s for s in services_data if s[1] == "DE - Otrzymano dokumenty"]
            uninformed_or_unsent = [s for s in services_data if (s[6] == "Nie" or s[7] == "Nie") and s[1] == "DE - Rozliczono"]
            downpayment_services = [s for s in services_data if len(s) > 16 and s[16] != "Opłacony"]

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
            
            # Klienci z usługami 'DE - Otrzymano dokumenty'
            if received_docs_services:
                rows_for_df = []
                for s in received_docs_services:
                    full_name_raw = s[0]
                    full_name = extract_name(full_name_raw)  # Oczyszczone imię i nazwisko
                    biuro = clients_dict.get(full_name)

                    # Pobieranie wartości z zabezpieczeniem przed IndexError
                    rok = s[2] if len(s) > 3 else ""
                    opiekun = s[4] if len(s) > 4 else ""
                    uwagi = s[5] if len(s) > 5 else ""
                    konto_elster = s[48] if len(s) > 6 else ""
                    ogr_ob_podatkowy = s[49] if len(s) > 7 else ""

                    row_data = [full_name, s[1], biuro, rok, opiekun, uwagi, konto_elster, ogr_ob_podatkowy]
                    rows_for_df.append(row_data)

                received_docs_df = pd.DataFrame(
                    rows_for_df,
                    columns=["Imię i Nazwisko", "Status", "Biuro", "Rok", "Opiekun", "UWAGI", "Konto Elster", "Ogr. ob. podatkowy"]
                )
                received_docs_df.index = received_docs_df.index + 1

                ilosc_otrzymano_dokumenty = len(received_docs_df)
                st.markdown(
                    f"<h3 style='color: #545454; font-weight:600;font-size:20px'>Klienci z usługami "
                    f"<span style='color: #03ab0f; font-weight:700;font-size:30px'>DE - Otrzymano dokumenty</span> "
                    f"(ilość: {ilosc_otrzymano_dokumenty})</h3>",
                    unsafe_allow_html=True
                )

                # Stylizacja tabeli (jeśli funkcja highlight_row_if_status jest zaimplementowana)
                received_docs_services_styled = received_docs_df.style.apply(highlight_row_if_status, axis=1)
                st.dataframe(received_docs_services_styled)
            else:
                ilosc_otrzymano_dokumenty = 0
                st.markdown(f"<h3 style='color: #545454; font-weight:600;font-size:20px'>Klienci z usługami <span style='color: #03ab0f; font-weight:700;font-size:30px'>DE - Otrzymano dokumenty</span> (ilość: {ilosc_otrzymano_dokumenty})</h3>", unsafe_allow_html=True)
  
            #Klienci z usługami 'DE - Niekompletny zestaw'
            if incomplete_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 1, 2, 4, 5, 48,49]  # Indeksy kolumn 1, 2, 3, 5, 7
                incomplete_services_filtered = [[row[i] for i in selected_columns] for row in incomplete_services]
                incomplete_services_df = pd.DataFrame(incomplete_services_filtered, columns=["Imię i Nazwisko", "Status", "Rok", "Opiekun", "UWAGI", "Konto Elster", "Ogr. ob. podatkowy"])
                # Numerowanie wierszy od 1
                incomplete_services_df.index = incomplete_services_df.index + 1
                
                ilosc_niekompletny_zestaw = len(incomplete_services_df)
                st.markdown(f"<h3>Klienci z usługami <span style='color: #ed3434; font-weight:700;font-size:30px'> DE - Niekompletny zestaw </span> ({ilosc_niekompletny_zestaw})</h3>", unsafe_allow_html=True)
                incomplete_services_styled = incomplete_services_df.style.apply(highlight_row_if_status, axis=1)
                st.dataframe(incomplete_services_styled)    
            else:
                ilosc_niekompletny_zestaw = 0
                st.markdown(f"<h3>Klienci z usługami <span style='color: #ed3434; font-weight:700;font-size:30px'> DE - Niekompletny zestaw </span> ({ilosc_niekompletny_zestaw})</h3>", unsafe_allow_html=True)
  
            #Klienci do wysłania
            if uninformed_or_unsent:
                rows_for_df = []
                for s in uninformed_or_unsent:
                    full_name_raw = s[0]
                    full_name = extract_name(full_name_raw)  # Oczyszczone imię i nazwisko
                    biuro = clients_dict.get(full_name)

                    # Pobieranie wartości z zabezpieczeniem przed IndexError
                    rok = s[2] if len(s) > 3 else ""
                    opiekun = s[4] if len(s) > 4 else ""
                    uwagi = s[5] if len(s) > 5 else ""
                    poinformowany = s[6] if len(s) > 6 else ""
                    wyslany = s[7] if len(s) > 6 else ""

                    row_data = [full_name, s[1], biuro, rok, poinformowany, wyslany, uwagi]
                    rows_for_df.append(row_data)
                # Upewnij się, że liczba kolumn pasuje do danych
                uninformed_or_unsent_df = pd.DataFrame(
                        rows_for_df,
                        columns=["Imię i Nazwisko", "Status", "Biuro", "Rok", "Poinformowany", "Wysłany", "UWAGI"]
                    )
                ilosc_niepoinformowany = len(uninformed_or_unsent_df)
                st.subheader(f"Klienci do wysłania (ilość: {ilosc_niepoinformowany})")    
                uninformed_or_unsent_styled = uninformed_or_unsent_df.style.apply(highlight_status, axis=1)
                st.dataframe(uninformed_or_unsent_styled)
            else:
                ilosc_niepoinformowany = 0
                st.subheader(f"Klienci do wysłania (ilość: {ilosc_niepoinformowany})")    
 
            #Klienci z zaliczką
            if downpayment_services:
                # Upewnij się, że liczba kolumn pasuje do danych
                selected_columns = [0, 15,16, 17, 18, 19,5, 20]  # Indeksy kolumn 1, 2, 3, 5, 7
                downpayment_services_filtered = [[row[i] for i in selected_columns] for row in downpayment_services]
                downpayment_services_df = pd.DataFrame(downpayment_services_filtered, columns=["Imię i Nazwisko","Cena", "Status płatności", "Zapłacono", "Forma zapłaty", "Nr. faktury", "Uwagi","Data wystawienia faktury"])
            
                ilosc_klienci_z_zaliczka = len(downpayment_services_df)
                st.subheader(f"Klienci z zaliczką lub z statusem nieopłacono ({len(downpayment_services_df)})")
                st.dataframe(downpayment_services_df)
            else:
                ilosc_klienci_z_zaliczka = 0
                st.subheader(f"Klienci z zaliczką lub z statusem nieopłacono ({ilosc_klienci_z_zaliczka})")         
        elif choice == "Cały excel":
            st.subheader("Cały arkusz ZP status") 
            df = fetch_full_status_data()
            df_unique = make_unique_columns(df)  # Ensure unique column names
            edited_df = st.data_editor(df_unique)

            if st.button("Zapisz zmiany"):
                update_status_data(edited_df)
                st.success("Dane zostały zaktualizowane")
        elif choice == "Edytuj klienta":
            edytuj_klienta()
        elif choice == "Edytuj usługę":
            edytuj_usluge()
        elif choice == "Edytuj usługę - Kamil":
            edytuj_usluge_skrocona()
    
if __name__ == "__main__":
    main()
