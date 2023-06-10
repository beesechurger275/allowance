
## INSTALLATION INSTRUCTIONS

1. Download .zip file and extract to folder
2. Install dependencies:
    - Create virtual environment

    > `python -m venv venv`

    - Activate virtual environment

    Windows:

    > `venv\Scripts\Activate.ps1`

    macOS/Linux

    > `venv/bin/activate`

    - Install flask

    > `pip install flask`
    
    or

    > `python -m pip install flask`

3. Create necessary files
    - Create file in directory named data.sql

    > `touch data.sql`

    - Create secretkey.txt and make secret key

    > `python -c 'import secrets; print(secrets.token_hex())' > secretkey.txt`

    **Do not reveal this secret key.**

4. Create default admin account
    - Change username and password in *createadminaccount.py* if desired
    - Run createadminaccount.py

    > `python createadminaccount.py`

    *by default, username is admin, password is admin*

5. Run flask server
    
    > `python -m flask run`

    for debug mode (autorefresh when changes are made):

    > `python -m flask --debug run`

    ###### Note: Do not use development server in production. Use a production WSGI server instead

For more information, [read the flask documentation.](https://flask.palletsprojects.com/en/2.3.x/)