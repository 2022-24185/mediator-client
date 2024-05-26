#!/bin/bash
# Before running: make sure to run chmod +x setup_dev.sh from project root.
# To run: in terminal, run ./setup_dev.sh

# Check if Python 3 and pip are installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    case "$(uname -s)" in
        Darwin)
            brew install python3
            ;;
        Linux)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            echo "Please install Python 3 manually using the official installer."
            ;;
        *)
            echo "Unknown operating system. Please install Python 3 manually."
            exit 1
            ;;
    esac
else
    echo "Python 3 is already installed."
fi

# Deactivate any other active Python environments
echo "Deactivating any other active Python environments..."
deactivate || true

# Create a virtual environment if it doesn't exist
VENV_DIR="social_regulator_env"
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating a virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Ensure pip is up to date
echo "Ensuring pip3 is up to date..."
#pip install --upgrade pip
pip install pip==23.3.2

# Install requirements
REQUIREMENTS="requirements.txt"
if [ -f "$REQUIREMENTS" ]; then
    echo "Installing requirements from $REQUIREMENTS..."
    echo "Cython<3" > cython_constraint.txt
    PIP_CONSTRAINT=cython_constraint.txt pip install
    pip3 install -r $REQUIREMENTS
else
    echo "No requirements.txt file found, skipping dependency installation."
fi

# Download the VADER sentiment analysis lexicon
echo "Downloading the VADER sentiment analysis lexicon..."
python3 -m nltk.downloader vader_lexicon
if [ $? -ne 0 ]; then
    echo "Error downloading VADER sentiment analysis lexicon. Exiting..."
    exit 1
fi

# Install tkinter if necessary (Python GUI)
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter is not installed. Installing based on your OS..."
    case "$(uname -s)" in
        Darwin)
            echo "Detected macOS. Installing tkinter..."
            brew install python-tk
            ;;
        Linux)
            echo "Detected Linux. Installing tkinter..."
            sudo apt-get install python3-tk
            ;;
        *)
            echo "Auto-installation of tkinter failed. Please install it manually."
            exit 1
            ;;
    esac
else
    echo "tkinter is already installed."
fi

echo "Development environment setup is complete."
