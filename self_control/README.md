# **Self Control Software**

A **Kivy-based experiment application** designed to control an operant conditioning chamber. This application is paired with a **Tkinter support launcher** to start the Kivy experiment. The system supports hardware integrations like feeders, house lights, and touch panels. 

The project is well-structured, modular, and includes clear separation of services, components, and utilities.

---

## **📁 Project Structure**
```
self_control_software/
├── main.py                  # Entry point for the Kivy app
├── config.py                # App configuration file (graphics, DB credentials, etc.)
├── requirements.txt         # Python dependencies
├── README.md                # Instructions for running the project
│
├── assets/                  # Images, sounds, etc.
│   ├── audio/
│   └── images/
│
├── services/                # Handles logic for feeders, lights, DB, and monitoring
│   ├── usb_monitor.py       # Monitors USB devices
│   ├── feeder.py            # Feeder service
│   ├── house_light.py       # House light service
│   ├── writer.py            # Writes log data
│   └── random_number_db.py  # Database service to manage PostgreSQL interactions
│
├── components/              # Custom Kivy components and layouts
│   ├── buttons.py           # Custom Kivy buttons (green, red, etc.)
│   └── experiment_layout.py # Main Kivy experiment layout
│
├── utils/                   # Utility functions (logging, helpers, etc.)
│   ├── distance.py          # Contains the distance_from function
│   ├── serializer.py        # Handles date/time serialization
│   └── logger.py            # Logger for the application
│
├── kv/                      # Kivy layout files
│   └── self_control.kv      # Kivy layout for the main application
│
├── tk_support/              # Supportive Tkinter app (optional)
│   ├── launcher.py          # Launches the Kivy app via a GUI
│   ├── config.py            # Configurations for the launcher
│   ├── controllers.py       # Controller logic for launcher
│   └── views.py             # View logic for launcher UI
│
└── tests/                   # Automated tests for the Kivy and Tkinter apps
```

---

## **🚀 Features**
- **Hardware Control**: Feeder, House Light, and Touch Panel control.
- **Dynamic UI**: Interactive Kivy interface with custom buttons, warnings, and signals.
- **Data Logging**: Logs user interactions and experiment events.
- **Database Integration**: Connects to **PostgreSQL** to store and retrieve experimental data.
- **Modular Structure**: Clear separation of concerns using components, services, and utilities.
- **Tkinter Launcher**: An optional **Tkinter app** to start the Kivy experiment.
  
---

## **🛠️ Prerequisites**
Ensure you have the following software installed:
- **Python 3.8+**
- **PostgreSQL** (for the database)
- **Kivy** (for the UI)
- **Psycopg2** (for PostgreSQL integration)
- **USB Monitor** (for device monitoring)

---

## **📦 Installation**
### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/self_control_software.git
cd self_control_software
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

> **Note:** Ensure **PostgreSQL** is running and your database credentials match those in `config.py`.

---

## **🚀 Usage**
You can start the app in two ways:
1. **Run Kivy app directly**:
    ```bash
    python main.py <experiment_id>
    ```

    Example:
    ```bash
    python main.py 123  # Runs experiment with ID 123
    ```

2. **Launch from Tkinter support app**:
    ```bash
    python tk_support/launcher.py
    ```

    This opens a **graphical interface** where you can select the experiment ID and start the experiment.

---

## **🔧 Configuration**
### **1. Database**
The **database credentials** are stored in `config.py`:
```python
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'pigeon123!'
}
```
> **Update this file with your database name, user, and password.**

### **2. Window Position & Size**
You can change the **window position** and **size** in `config.py`:
```python
from kivy.config import Config
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '0')
Config.set('graphics', 'left', '-1440')
Config.set('graphics', 'fullscreen', 'auto')
```

---

## **📚 How It Works**
1. **Tkinter GUI**: Users select the experiment and start it.
2. **Kivy App Launch**: The main Kivy window opens with a custom UI.
3. **Hardware Control**: The feeder, house light, and warning system are activated.
4. **Data Logging**: Every event is logged to a file (via **Writer service**).
5. **Experiment End**: The experiment ends, and the results are generated.

---

## **🧩 Services Explained**
### **1. Feeder**
The feeder is controlled using **Feeder service**. It activates/deactivates the feeder based on experiment logic.

### **2. House Light**
The **HouseLight** service controls the house light during different stages of the experiment (e.g., warning signals, punishment, or end-of-experiment).

### **3. USB Monitor**
The **USBMonitor** tracks if a USB touch panel is connected. It triggers the necessary event when a connection is lost or restored.

### **4. Database**
Data for the experiment and subject are stored in a **PostgreSQL database**. The service file `random_number_db.py` handles queries to the database.

---

## **📋 Event Flow**
1. **Start Experiment**: The user launches the experiment.
2. **Feed**: The feeder is activated at certain points.
3. **Warning**: Warnings are displayed based on experimental conditions.
4. **Punishment**: The screen turns off for punishments.
5. **End**: The experiment concludes, and a PDF summary is generated.

---

## **📑 Logs**
All interactions are logged via the **Writer service**. Example logs include:
- **Peck Data**
- **Button Presses**
- **Warning Triggers**
- **Reinforcements and Punishments**

---

## **🧪 Testing**
To run the automated tests, navigate to the **tests** folder and run:
```bash
pytest
```

> Ensure all components (like database) are available when testing.

---

## **🔍 Troubleshooting**
| **Issue**          | **Solution**                                 |
|-------------------|-----------------------------------------------|
| No PostgreSQL     | Make sure PostgreSQL is installed and running.|
| Can't Connect to DB| Check database credentials in `config.py`.   |
| No Kivy App Window| Ensure all dependencies are installed.        |
| Feeder Not Working| Check if feeder is connected properly.       |
| USB Panel Issue   | Check USB connection for the touch panel.     |

---

## **🔗 Important Files**
| **File**             | **Description**                             |
|---------------------|---------------------------------------------|
| `main.py`            | Entry point for the Kivy app.               |
| `tk_support/launcher.py` | GUI launcher for the Kivy app.         |
| `services/`          | Service logic (DB, feeder, light, etc.).    |
| `components/`        | Custom Kivy components (buttons, layout).   |
| `requirements.txt`   | Python dependencies.                        |

---

## **🌐 Resources**
- **Kivy Documentation**: [https://kivy.org/doc/stable/](https://kivy.org/doc/stable/)
- **PostgreSQL**: [https://www.postgresql.org/](https://www.postgresql.org/)

---

## **🤝 Contributing**
We welcome contributions to improve this app! If you'd like to contribute, follow these steps:
1. **Fork** this repository.
2. **Create a branch**: 
    ```bash
    git checkout -b feature/new-feature
    ```
3. **Commit changes**: 
    ```bash
    git commit -m "Added a new feature"
    ```
4. **Push to branch**: 
    ```bash
    git push origin feature/new-feature
    ```
5. **Create Pull Request**: Submit your PR for review.

---

## **📜 License**
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

If you have any questions or need further assistance, feel free to open an **issue** in the repository. 😊