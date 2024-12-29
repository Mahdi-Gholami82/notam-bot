# **Iranian NOTAMs Bot**

This project consists of two scripts that work together to automate the process of sending Iranian NOTAM (Notice to Air Missions) information to a Telegram channel.  
The bot provides both text updates and visualizations of specific NOTAM regions.

## **Features**

1. **NOTAM Text Updates (`sendNotamText.py`)**  
   - Sends Iranian NOTAMs directly to a specified Telegram channel as text messages.  
   - Keeps subscribers updated with the latest aviation notices.

2. **NOTAM Region Visualization (`sendMap.py`)**  
   - Highlights and visualizes specific NOTAM regions, including:  
     - RPA (Remotely Piloted Aircraft)  
     - Gun Firing zones  
     - Rocket Launch zones  
   - Generates a map image with the highlighted areas and sends it to the Telegram channel.

## **Dependencies**  
Ensure the following libraries are installed before running the scripts:
- `beautifulsoup4`
- `folium`
- `selenium`
- `python-telegram-bot`
- `requests`
- `lxml`

## **Setup**
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure the Telegram API token and chat ID in the `config.py` file.

4. Run the `initialize_db.py` file.
   ```bash
   python3 initialize_db.py
   ```

3. Use Cron jobs to schedule running both scripts. (To prevent overlapping Cron jobs, you can use a tool like Flocker.)
