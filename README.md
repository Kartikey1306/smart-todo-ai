# Smart Todo List - AI-Powered Task Management

Welcome to the Smart Todo List, a full-stack application that combines a powerful Django REST Framework backend with a sleek Next.js frontend. This isn't just another todo app; it's an intelligent assistant designed to help you manage your tasks, understand your priorities, and stay ahead of your schedule using the power of AI.

## 📸 Screenshots

![Screenshot 2025-07-05 215343](https://github.com/user-attachments/assets/6175c10a-3fd1-40e8-bb47-70694a27aea3)

![Screenshot 2025-07-05 215358](https://github.com/user-attachments/assets/3bb606e7-dec6-45e3-8978-e20c72245969)
![Screenshot 2025-07-06 013259](https://github.com/user-attachments/assets/fbc05b92-6727-4ba9-a450-eafc235eacc2)
![Screenshot 2025-07-06 013315](https://github.com/user-attachments/assets/140bab7e-ded9-4870-afa9-e4206bc29521)

![Screenshot 2025-07-06 013324](https://github.com/user-attachments/assets/7fca09c1-d039-42ab-aa8f-e3df966a8368)
![Screenshot 2025-07-06 013339](https://github.com/user-attachments/assets/35cb2bb0-6954-465d-8592-ead349a1ba64)

Here's a glimpse of the clean and intuitive user interface you'll be working with.

| Dashboard Overview                                                                                             | Task Management View                                                                                             | AI Insights & Recommendations                                                                                             |
| -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| ![](/placeholder.svg?height=400&width=600&query=Clean+dashboard+with+statistical+cards+for+task+completion+rate) | ![](/placeholder.svg?height=400&width=600&query=Modern+task+list+view+with+priorities+and+deadlines)             | ![](/placeholder.svg?height=400&width=600&query=AI-powered+task+recommendations+and+workload+analysis+section)           |
| A high-level view of your productivity with key stats.                                                         | Manage your tasks with AI-suggested priorities and context tags.                                                 | Discover new tasks suggested by the AI based on your recent context.                                                      |

## ✨ Key Features

-   **🧠 AI-Powered Prioritization**: Automatically suggests task priorities based on content and context.
-   **🗣️ Natural Language Processing**: Create tasks by simply writing what you need to do.
-   **🤖 Context-Aware Recommendations**: The AI analyzes your notes and emails to suggest tasks you might have missed.
-   **📊 Workload Analysis**: Get AI-driven insights into your productivity and potential bottlenecks.
-   **⚡️ Asynchronous Processing**: Heavy AI operations run in the background using Celery, ensuring the UI remains fast and responsive.

## 🔧 Local Setup and Installation

Follow these steps to get the application running directly on your local machine.

### Prerequisites

Before you begin, you must have the following software installed on your system:

-   **Node.js** (v18 or newer)
-   **Python** (v3.11 or newer)
-   **PostgreSQL** (v12 or newer)
-   **Redis** (v6 or newer)
-   An **OpenAI API Key**

> **Tip:** For macOS, a simple way to install PostgreSQL and Redis is using [Homebrew](https://brew.sh/):
> `brew install postgresql redis`

### 1. Clone the Repository

\`\`\`bash
git clone <your-repository-url>
cd smart-todo-list
\`\`\`

### 2. Backend Setup (Django)

First, set up the Python environment and backend services.

**a. Start Database and Cache Services**

Make sure your local PostgreSQL and Redis servers are running. If you installed them with Homebrew, you can start them with:

\`\`\`bash
# Start PostgreSQL
brew services start postgresql

# Start Redis
brew services start redis
\`\`\`

**b. Create the Database**

You need to create a database for the application. You can do this using the `psql` command-line tool.

\`\`\`bash
# Open the PostgreSQL command line
psql postgres

# Run the following SQL command to create the database
CREATE DATABASE smart_todo;

# Exit psql
\q
\`\`\`

**c. Set Up the Python Environment**

\`\`\`bash
# Navigate to the backend directory
cd smart-todo-ai # Or your backend folder name

# Create and activate a virtual environment
CREATE DATABASE smart_todo;
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt
\`\`\`

**d. Configure Environment Variables**

\`\`\`bash
# Create a .env file from the example
cp .env.example .env
\`\`\`
Now, open the `.env` file and update it with your local database credentials and your OpenAI API key. It should look something like this:

\`\`\`
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Your local database configuration
DB_NAME=smart_todo
DB_USER=your_postgres_username # Often 'postgres' or your system username
DB_PASSWORD=your_postgres_password # Set this when you installed PostgreSQL
DB_HOST=localhost
DB_PORT=5432

# Your OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Local Redis URL
REDIS_URL=redis://localhost:6379/0
\`\`\`

**e. Run Database Migrations and Seeding**

\`\`\`bash
# Apply the database schema
python manage.py migrate

# Create a default admin user
python scripts/create_superuser.py

# Seed the database with sample data
python scripts/seed_data.py
\`\`\`

**f. Start the Backend Services**

You will need to run the Django server and the Celery worker in **two separate terminal windows**.

\`\`\`bash
# --- In Terminal 1: Start the Django Server ---
# (Make sure your virtual environment is active)
python manage.py runserver
\`\`\`

\`\`\`bash
# --- In Terminal 2: Start the Celery Worker ---
# (Navigate to the backend folder and activate the venv)
celery -A smart_todo worker -l info
\`\`\`

Your backend is now running at `http://localhost:8000`.

### 3. Frontend Setup (Next.js)

Finally, set up and run the Next.js frontend in a **third terminal window**.

\`\`\`bash
# Navigate back to the root project directory
cd ..

# Install frontend dependencies
npm install

# Start the Next.js development server
npm run dev
\`\`\`

Your frontend is now running at `http://localhost:3000` and is connected to your local backend. You should see the pre-loaded data and be able to interact with all the application's features.
