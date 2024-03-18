#!/bin/bash

PROJECT_DIR="Projet7_Implementez_un_modele_de_scoring"

if [ -d "$PROJECT_DIR" ]; then
  echo "$PROJECT_DIR found.we are going to pull"
  cd $PROJECT_DIR
  git add .
  git pull origin develop
  echo "Activating venv"
  source venv/bin/activate
  echo "Updating pip"
  python3 -m pip install --upgrade pip
  echo "Installing dependency"
  python3 -m pip install -r requirements.txt
  echo "Stopping streamlit and flask"
  ps aux | grep -i 'streamlit run web.py' | awk {'print $2'} | head -n 1 | xargs kill -9
  ps aux | grep -i 'python3 backend.py' | awk {'print $2'} | head -n 1 | xargs kill -9
  rm flask.log streamlit.log
  echo "Running the app"
  python3 backend.py >> flask.log 2>&1 &
  streamlit run web.py >> streamlit.log 2>&1 &
else
  echo "Installing python3 pip"
  sudo apt install python3-pip -y
  echo "Installing python3 env"
  sudo apt install python3-venv -y
  echo "$PROJECT_DIR not found. we are going to clone"
  git clone -b develop https://github.com/KGBOGNING/Projet7_Implementez_un_modele_de_scoring.git
  echo "Change directory to enter in project"
  cd $PROJECT_DIR
  echo "Create virtual env"
  python3 -m venv venv
  echo "Activating venv"
  source venv/bin/activate
  echo "Updating pip"
  python3 -m pip install --upgrade pip
  echo "Installing dependency"
  python3 -m pip install -r requirements.txt
  echo "Running the app"
  python3 backend.py >> flask.log 2>&1 &
  streamlit run web.py >> streamlit.log 2>&1 &
fi

