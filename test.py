import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['123', '456']).generate()
print(hashed_passwords)