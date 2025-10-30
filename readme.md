# Analytics Workflow Demo: From Local API to Data Warehouse

Welcome! This project is a complete, hands-on example of a professional analytics workflow. 

---

## Part 1: Set Up the Local API Server (The "Data Source")

First, we'll simulate a real-world data source (like Workday or SAP) by creating a local API server. This server will run on your computer and serve your `roster.csv` and `work.csv` files. 
**IF YOU JUST WANT TO LOAD THE DATA AND PLAY WITH IT IN TABLEAU SEE PART 4**

### Prerequisites:
You'll need **Node.js**.
* **What it is:** A program that lets you run JavaScript code outside of a web browser (like our `server.js` script).
* **How to get it:** Download and install it from [nodejs.org](https://nodejs.org/).

### Instructions:

1.  **Open Your Terminal:**
    * **Windows:** Open the Start Menu and type `cmd` (Command Prompt) or `PowerShell`.
    * **Mac:** Press `Cmd + Space`, type `Terminal`, and press Enter.

2.  **Navigate to This Project Folder:**
    Use the `cd` (Change Directory) command. For example, if your folder is on your Desktop:
    ```bash
    cd Desktop/Your-Project-Folder
    ```
    (Replace `Your-Project-Folder` with the real name).

3.  **Install the Server Libraries:**
    Now we'll use `npm` (Node Package Manager), which was installed with Node.js. Type this command and press Enter:
    ```bash
    npm install
    ```
    *This reads the `package.json` file and automatically downloads the libraries we need (`json-server` and `csv-parser`). You only need to do this once.*

4.  **Start the Server!**
    Now, run the server with this command:
    ```bash
    npm start
    ```
    You should see a "Server is running!" message with a list of "Available endpoints." This terminal is now running your API.

**IMPORTANT: Leave this terminal window open!** Your API server will stop running if you close it.

---

## Part 2: Run the ETL Pipeline (The "Data Engine")

Now that your API is running, we'll use Python to Extract, Transform, and Load the data. We'll do this in a *second*, separate terminal window.

### Prerequisites:
You'll need **Python** and a few libraries.
* **How to get it:** If you don't have it, download it from [python.org](https://python.org/) or install the [Anaconda distribution](https://www.anaconda.com/download).

### Instructions:

1.  **Open a *Second* Terminal:**
    Leave your *first* terminal (the one running the server) alone. Open a brand new terminal window.

2.  **Navigate to the Project Folder:**
    Just like before, use the `cd` command to go to your project folder:
    ```bash
    cd Desktop/Your-Project-Folder
    ```

3.  **Install the Python Libraries:**
    We'll use `pip` (Python's package installer) to get the libraries for this script.
    ```bash
    pip install pandas requests sqlalchemy
    ```
    *You only need to do this once.*

4.  **Run the ETL Script!**
    Now, run the Python script:
    ```bash
    python run_etl_to_sqlite.py
    ```
    You will see the script print its progress:
    * `Querying API for Roster data...` (Extract)
    * `Cleaning column names...` (Transform)
    * `Joining data on 'userid'...` (Transform)
    * `Uploading joined data to table...` (Load)
    * `✅ Success!`

When it's finished, **look in your project folder.** You will see a new file: `my_local_database.db`. **This is your data warehouse!**

---

## Part 3: Connect Tableau (The "Dashboard")

Now you have a clean, reliable database file ready for analysis.

### Prerequisites:
You'll need **Tableau Desktop**.
* **How to get it:** As a student, you can get a free 1-year license from the **Tableau for Students** program.
* **Link:** [https://www.tableau.com/academic/students](https://www.tableau.com/academic/students)
* **Note:** You will need to verify your student status to get the free license.


1.  Open Tableau Desktop.
2.  On the "Connect" panel (on the left), click **"More..."**
3.  Select **"SQLite"** from the list.
4.  A file browser will open. Navigate to your project folder and select the `my_local_database.db` file.
5.  Tableau is now connected! You will see your table, `quac_tech_demo`, in the data pane.
6.  Drag `quac_tech_demo` onto the canvas.

You're all set! You can now use this clean data to build your dashboard, create the parameters, and add the dynamic calculated fields we talked about.

---

## (Alternative) Part 4: Tableau-Only Practice


### Prerequisites:
You'll need **Tableau Desktop**.
* **How to get it:** As a student, you can get a free 1-year license from the **Tableau for Students** program.
* **Link:** [https://www.tableau.com/academic/students](https://www.tableau.com/academic/students)
* **Note:** You will need to verify your student status to get the free license.


If you want to skip the API server and Python script, you can practice joining and cleaning data *directly in Tableau*.



This is a great way to understand the *data* and *visualization* parts of the project.

1.  Open Tableau Desktop.
2.  On the "Connect" panel, click on **"Text file"**.
3.  Navigate to the `data/` folder and select `roster.csv`.
4.  In the "Data Source" tab, you'll see the `roster` table. Click the **"Add"** button (next to "Connections").
5.  Select **"Text file"** again, navigate to `data/`, and select `work.csv`.
6.  Tableau will automatically try to join them. Click on the "noodle" (the join icon) between the two tables.
7.  Set up the join:
    * In the "Roster" (left) column, select **`userid`**.
    * In the "Work" (right) column, select **`userid`**.
    * Make sure it's an **"Inner"** join.
8.  Click "Go to Worksheet."

You now have the same joined data as the Python script, and you can begin building your heatmap and calculated fields!
