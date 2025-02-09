import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def service_exists(klient, statusDE, rok):
    # Implement the logic to check if the service already exists
    pass

def add_service(klient, statusDE, rok,
                delegacje_zagraniczne):
    if service_exists(klient, statusDE, rok):
        st.markdown(f'<span style="border-radius:10px;padding:18px;background-color:rgba(255, 43, 43, 0.09);">Usługa dla klienta:<span style="font-size:18px; font-weight:bold;color:lightcoral"> {klient} </span>o statusie: <span style="font-size:18px; font-weight:bold;"> {statusDE}</span> za rok:<span style="font-size:18px; font-weight:bold;">  {rok}</span> już ISTNIEJE', unsafe_allow_html=True)
        return
    new_row = [
        klient, statusDE, rok, zwrot, opiekun, uwagi, poinformowany, wyslany, fahrkosten, ubernachtung, h24, h8, wKabinie,
        anUndAb, dzieci, cena, statusPlatnosciu, zaplacono, formaZaplaty, nrfaktury, dataWystawieniaFaktury, zarobkiMezaEuro,
        zarobZonyEuro, nr22, nr23, nr25, nr26, nr27, pracodawca, chorobowe, klasaPIT1, brutto1, podatek1, dopłata1, kościelny1,
        kurzarbeitergeld1, klasaPIT2, brutto2, podatek2, dopłata2, kościelny2, kurzarbeitergeld2, klasaPIT3, brutto3, podatek3,
        dopłata3, kościelny3, kurzarbeitergeld3, kontoElster, ogrObPodatkowy, aktualny_stan_zamieszkania, miejsce_urodzenia,
        kraj_urodzenia, narodowosc, KlasaPITmałżonka, Bruttomałżonka, Podatekmałżonka, Dopłatamałżonka, Kościelnymałżonka,
        Kurzarbeitergeldmałżonka, Nr22malzonka, Nr23malzonka, Nr25malzonka, Nr26malzonka, Nr27malzonka, Pracodawcamalzonka,
        Chorobowemalzonka, Bezrobociepodatnika, Bezrobociemałżonka, delegacje_zagraniczne
    ]
    sheet2.append_row(new_row)
    st.success("Nowa usługa została dodana")

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

# Sekcja dodawania usługi
if __name__ == "__main__":
    st.title("Dodaj nową usługę")

    choice = st.selectbox("Wybierz akcję", ["Dodaj usługę", "Inna akcja"])
    if choice == "Dodaj usługę":
        st.subheader("Dodaj nową usługę")
        st.subheader("Zaznacz odpowiednie opcje")

        all_clients = fetch_clients()
        delegacje = st.checkbox("Czy są delegacje zagraniczne", key="delegacje")
        num_delegacje = st.number_input("Ile krajów?", min_value=1, max_value=10, step=1, key="num_delegacje")
        st.subheader("Wypełnij dane usługi")
        with st.form(key="status_form"):
            klient = st.selectbox("Podatnik", all_clients, key="klient")
            statusDE = st.selectbox("Status DE", ["", "DE - Niekompletny zestaw", "DE - Otrzymano dokumenty", "DE - Rozliczono"], key="statusDE")
            rok = st.selectbox("Rok", ['2024','2023', '2022', '2021', '2020', '2019', '2018'], key="rok")

            delegacje_zagraniczne = []
            if delegacje:
                st.write("Dodaj kraje i ilość dni delegacji")
                

                for i in range(num_delegacje):
                    st.write(f"Delegacja {i+1}")
                    kraj = st.text_input(f"Kraj {i+1}", key=f"kraj_{i}")
                    ilosc_dni_delegacji = st.number_input(f"Ilość dni {i+1}", min_value=1, key=f"ilosc_dni_{i}")
                    delegacje_zagraniczne.append((kraj, ilosc_dni_delegacji))
            
            submit_status = st.form_submit_button(label='Dodaj usługę')

        if submit_status:
            if not klient or not statusDE or not rok:
                st.error("Podanie danych klienta, Statusu DE oraz roku rozliczenia jest wymagane")
            else:
                delegacje_str = "; ".join([f"{kraj}:{dni}" for kraj, dni in delegacje_zagraniczne])
                add_service(klient, statusDE, rok,
                            delegacje_str)
