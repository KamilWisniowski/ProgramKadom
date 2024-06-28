import streamlit as st

# Tytuł aplikacji
st.title('Formularz Informacyjny')

# Tworzenie formularza wyboru stanu cywilnego
with st.form(key='marital_status_form'):
    marital_status = st.selectbox('Stan cywilny:', ['kawaler', 'żonaty', 'rozwiedziony', 'panienka', 'mężatka'])
    submit_status = st.form_submit_button(label='Wybierz stan cywilny')

# Tworzenie głównego formularza
with st.form(key='info_form'):
    first_name = st.text_input('Imię:')
    last_name = st.text_input('Nazwisko:')
    
    if marital_status == 'żonaty':
        last_name_wife = st.text_input('Nazwisko żony:')
        marriage_date = st.date_input('Data ślubu:')
    else:
        last_name_wife = None
        marriage_date = None

    submit_info = st.form_submit_button(label='Submit')

# Obsługa przycisku submit
if submit_info:
    st.write(f"Imię: {first_name}")
    st.write(f"Nazwisko: {last_name}")
    st.write(f"Stan cywilny: {marital_status}")
    if marital_status == 'żonaty':
        st.write(f"Nazwisko żony: {last_name_wife}")
        st.write(f"Data ślubu: {marriage_date}")
