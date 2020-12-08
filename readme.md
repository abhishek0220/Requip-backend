# Requip Backend
[![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)

Requip is a buy and sell ecommerce website for the people of Indian Institute of Technology Jammu. Requip website is powered by Requip Backend APIs.

# API Documentation

## Authentication
Access to the Requip API is granted by JWT access token. To get access token you have to provide your username and password. The username and password used, is the same username and password you use to access the Recuip web or app interface. See **User APIs** for authentication API

- **[User APIs](/docs/user.md)**
- **[Saman APIs](/docs/saman.md)**

## Technology stack

- Python 3.7
- Flask framework
- Running on: Azure app service
- Media Server: Azure Blob Storage
- Database : MongoDB
- Deployment : Github Actions
    
# Instructions to Run locally and contribute
1. Install [Python](https://www.python.org/downloads/).
2. Clone this repository and open terminal, change directory to the repo.
3. Run `python -m venv venv` to create virtual environment.
4. Run `venv\Scripts\activate` command to activate virtual environment.
5. Run `pip install -r reqirements.txt` command to install dependencies.
6. Create a **.env** file in the folder, containing

```
MONGODB_URI = <token>
STORAGE = <azure_storage_token>
SENDGRID_API_KEY = <sendgrid_token>
FRONTEND = <frontend_location>
AZURE_COMPUTER_VISION = <Azure computer vision endpoint and key seperated by ; >
```
7. Create System Var `$env:FLASK_APP="application.py"`, `$env:FLASK_DEBUG=1` using terminal.
8. Enter `flask run` to create server.
9. Push the changes in a separate branch and create a pull request. After the PR is merged, it will be automatically deployed to Azure App Service via Github Actions.
<<<<<<< HEAD
=======


>>>>>>> b5fa3fe1b02c31725667d350e68791b72c8f8ed3
