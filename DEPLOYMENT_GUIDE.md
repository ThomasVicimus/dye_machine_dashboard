# Dye Machine Dashboard - Deployment Guide

This guide will help you set up the Dye Machine Dashboard application on a new PC using pip and pipenv.

## Prerequisites

1. **Python 3.10** - Make sure Python 3.10 is installed on the target PC
   - Download from: https://www.python.org/downloads/
   - During installation, make sure to check "Add Python to PATH"

2. **Git** (optional but recommended)
   - Download from: https://git-scm.com/downloads

## Option 1: Using Pipenv (Recommended)

Pipenv provides better dependency management and virtual environment handling.

### Step 1: Install Pipenv
```bash
pip install pipenv
```

### Step 2: Clone/Copy the Project
```bash
# If using Git:
git clone <your-repository-url>
cd dye_machine_dashboard

# Or manually copy all project files to a folder
```

### Step 3: Install Dependencies
```bash
# This will create a virtual environment and install all dependencies
pipenv install

# If you encounter any issues, try:
pipenv install --skip-lock
```

### Step 4: Activate the Environment
```bash
pipenv shell
```

### Step 5: Run the Application
```bash
python app.py
```

## Option 2: Using pip with venv

### Step 1: Create Virtual Environment
```bash
# Navigate to your project directory
cd dye_machine_dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

Choose one of the following options:

**Option 2a: Full requirements (exact versions)**
```bash
pip install -r requirements.txt
```

**Option 2b: Minimal requirements (recommended for new setups)**
```bash
pip install -r requirements-minimal.txt
```

### Step 3: Run the Application
```bash
python app.py
```

## Option 3: Direct pip install (Not Recommended)

If you want to install packages globally (not recommended):

```bash
pip install -r requirements-minimal.txt
python app.py
```

## Troubleshooting

### Common Issues and Solutions

1. **Python version mismatch**
   - Ensure Python 3.10 is installed
   - Check version: `python --version`

2. **Package installation fails**
   - Try upgrading pip: `pip install --upgrade pip`
   - Try installing with: `pip install --no-cache-dir -r requirements.txt`

3. **Permission errors on Windows**
   - Run command prompt as Administrator
   - Or use: `pip install --user -r requirements.txt`

4. **Dependency conflicts**
   - Use the minimal requirements file: `requirements-minimal.txt`
   - Create a fresh virtual environment

5. **Application doesn't start**
   - Check if all files are copied correctly
   - Ensure database connection settings are correct
   - Check for missing configuration files

### Windows-Specific Notes

- If you encounter SSL certificate issues, try:
  ```bash
  pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
  ```

- For better Windows compatibility, ensure Visual C++ redistributables are installed

## Verifying Installation

1. Activate your environment (pipenv shell or venv activation)
2. Run: `python -c "import dash, pandas, plotly; print('All dependencies loaded successfully!')"`
3. Start the application: `python app.py`
4. Open your browser and navigate to the URL shown in the terminal (usually http://127.0.0.1:8050)

## Application Structure

Key files you need to copy:
- `app.py` - Main application file
- `requirements.txt` / `Pipfile` - Dependencies
- `callbacks/` - Callback functions directory
- `layouts/` - Layout definitions
- `Database/` - Database related files
- Any configuration files

## Environment Variables

Make sure to set any required environment variables:
- `SECRET_KEY` - For Flask session security
- Database connection settings (if applicable)

## Next Steps

After successful installation:
1. Configure your database connection
2. Update any configuration files for your environment
3. Test all functionality
4. Set up any required services or scheduled tasks

## Getting Help

If you encounter issues:
1. Check the error messages carefully
2. Ensure all project files are present
3. Verify Python version compatibility
4. Try using the minimal requirements file first
5. Create a fresh virtual environment if problems persist 