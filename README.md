
## INSTALLATION INSTRUCTIONS

1. Download .zip file and extract to folder
2. Install dependencies:
    - Create virtual environment

        `python3 -m venv venv`

    - Activate virtual environment

        Windows PowerShell:

        `venv\Scripts\Activate.ps1`

        macOS/Linux

        `source venv/bin/activate`

    - Install flask

        `pip3 install flask`
        
        or

        `python3 -m pip install flask`

3. Create necessary files
    - Create file in directory named data.sql

        `touch data.sql`

    - Create secretkey.txt and make secret key

        `python3 -c 'import secrets; print(secrets.token_hex())' > secretkey.txt`

        **Do not reveal this secret key.**

4. Run flask server
    
    `python3 main.py`

    for debug mode (autorefresh when changes are made):

    `python3 -m flask --debug run`

    ###### Note: Do not use development server in production. Use a production WSGI server instead

5. Create admin account
    - Change username and password in *createadminaccount.py* if desired
    - Run createadminaccount.py

        `python createadminaccount.py [username] [password]`

For more information, [read the flask documentation.](https://flask.palletsprojects.com/en/2.3.x/)