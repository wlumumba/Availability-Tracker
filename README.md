# Availability Tracker

A Python-based tool for tracking availability across different sources. This program can be used to monitor availability of apartments, products, appointments, or anything with an API, and sends email notifications when changes are detected. It can be configured to run via cron job at user-specified intervals for automated monitoring.

## Purpose

- Tracks availability of multiple items simultaneously
- Modular design for easy addition of new trackers
- Email notifications for availability changes
- Docker support for containerized deployment

## Prerequisites

- Python 3.x
- uv (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd availability-tracker
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate
```

## Configuration

1. Create a `.env` file in the root directory with the following variables:
```
# Add your email configuration here (only supports AOL emails for now..)
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-email-password
EMAIL_RECIPIENT=recipient@example.com
```

## Usage

Run the program using:
```bash
python3 main.py
```

The program will:
1. Check availability for configured items
2. Process the results
3. Send email notifications if there are any changes

## Project Structure

- `main.py` - Main program entry point
- `trackers/` - Directory containing individual item trackers
- `email_service.py` - Handles email notifications
- `util.py` - Utility functions
- `Dockerfile` - Container configuration

## Docker Support

To run the program using Docker:

```bash
docker build -t availability-tracker .
docker run availability-tracker
```
