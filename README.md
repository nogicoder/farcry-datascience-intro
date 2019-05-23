# FarCry Data Science Introduction
A Repository for interacting with FarCry gamelog data

## Table of Contents
- [Introduction](#introduction)
- [Technologies](#technologies)
- [Requirements](#requirements)
- [Instruction](#instruction)

## Introduction
This repository contains a Python software used to interact with data logs from the game FarCry with additional files for Relational Database Management.  
This is an on-going project. The Project Dashboard on Trello can be found here: https://trello.com/b/KrUGRFTZ/farcry-data-science-intro

## Technologies
**This project is created with:**
- Python v3.7.3
- re module for Python (pre-packaged)
- csv module for Python (pre-packaged)
- postgres module for Python v2.2.2
- psycopg2 v2.8.2 for Python

**Software used in this projects:**
- Google Sheet by Google
- Navicat Data Modeler v2.1 (for modeling Database structure)
- DB Browser for SQLite (DB4S) v3.11.2 (for interacting with SQLite DB)
- TablePlus (optional, GUI for PostgreSQL)

## Requirements
Before running the app, it is required that you have these packages installed locally:
- Python v3.7.3 (with module re and csv as pre-packaged modules)
- postgres module for Python v2.2.2 (https://pypi.org/project/postgres/)
- psycopg2 v2.8.2 for Python (https://pypi.org/project/psycopg2/)
Please read the INSTALL.md for detail install instruction.

## Instruction
This app can be used to interact with the log data files from the game FarCry.  
- You can use the function from Waypoint 1 - 8 to parse the data from the log files
- The CSV exporting function in Waypoint 9 is for data interaction through Google Sheet in Waypoint 10-14. The link can be found here: https://bit.ly/2HnpPqz
- The database is modeled in the file: farcry.ndml using Navicat Data Modeler. You can open it through the software to modify the structure.
- The SQL Scripts from WP25.sql - WP45.sql contain scripts to query different data from SQLite Database. Use these scripts with DB4S of the version above to be supported with GUI better. You can also use sqlite3 CLI for interaction.
- The SQL Scripts from WP46.sql contain scripts to query data from PostgreSQL Database. Use TablePlus for GUI support or psql for CLI support.


Thank you for your time reading this document. Any feedback please response through my email: bach.mai@alumni.intek.edu.vn. Hope you have a good time with this software!
