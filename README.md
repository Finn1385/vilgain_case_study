# Installation Guide

This document outlines the necessary steps for installing and configuring the environment for this project. Follow these instructions carefully to ensure proper setup.

## Setting Up the Development Environment

### 1. Initialize the project

1. Create a new folder for the project and navigate to it
2. Clone Odoo repository (branch `18.0`: `git@github.com:odoo/odoo.git`
3. Check out Odoo to the `f91684d8178a41df321e781a81e6fce9df112346` commit.
4. Clone the project repository into the folder: `git@github.com:Finn1385/vilgain_case_study.git`
5. Create virtual environment for the project

```bash
mkdir odoo
cd odoo
git clone --branch 18.0 --single-branch git@github.com:odoo/odoo.git .
git checkout f91684d8178a41df321e781a81e6fce9df112346
git clone git@github.com:Finn1385/vilgain_case_study.git --depth 1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install PostgreSQL

1. Install PostgreSQL

```bash
sudo apt-get install postgresql
```

2. Create a new user and change the password

```bash
sudo -u postgres createuser --no-superuser --createdb --no-createrole <username>
sudo -u postgres psql -c "ALTER USER <username> WITH PASSWORD '<password>';"
sudo -u postgres createdb -O <username> <database_name>
```

### 3. Update odoo configuration

1. Copy the `vilgain_case_study/config/odoo.conf.example` file to `./odoo.conf` (root directory of the project)
2. Update the `db_user` and `db_name` fields in the `odoo.conf` file

### 4. Install Odoo

1. Install Odoo

```bash
./odoo-bin -c ./odoo.conf -i base
```

### 5. Open Odoo

1. Open Odoo in the browser (http://localhost:8069)

2. Login with the following credentials:

```
Email: admin
Password: admin
```

### 6. Install and setup the project addon

(In Odoo)

1. Go to the _Apps_ menu and install the `online_course` addon
2. Go to the _Settings -> Users & Companies -> Users -> Mitchell Admin -> Access Rights (tab)_ and add change the following:
   - In section _Other_ change _Online Course_ to **Teacher**
3. Refresh the whole page or log out and log in again

## Running the project

```bash
./odoo-bin -c ./odoo.conf
```

## Running the tests

```bash
./odoo-bin -c ./odoo.conf -i online_course --test-enable --stop-after-init
```
