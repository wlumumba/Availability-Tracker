# Availability Tracker

A Python-based tool for tracking availability across different sources. This program can be used to monitor availability of apartments, products, appointments, or anything with an API, and sends notifications when changes are detected. It can be configured to run via cron job at user-specified intervals for automated monitoring.

## Purpose

- Tracks availability of multiple items simultaneously
- Modular design for easy addition of new trackers
- Pushover notifications by default
- Optional per-tracker Discord channel routing

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

1. Create a `.env` file in the root directory with your Pushover credentials:
```
pushover_app_token=your-app-token
pushover_user_key=your-user-key
```

### Discord channels

Create an incoming webhook for each Discord channel that should receive tracker
notifications. Assign each channel an alias, then map tracker names to aliases:

```env
DISCORD_ROUTES=hai_ivy_track=HAI_JOBS,hai_equator_track=HAI_JOBS,sheridan=APARTMENTS
DISCORD_WEBHOOK_HAI_JOBS=https://discord.com/api/webhooks/...
DISCORD_WEBHOOK_APARTMENTS=https://discord.com/api/webhooks/...
```

Aliases may contain uppercase letters, numbers, and underscores. Each tracker can
appear once and route to one Discord channel. Trackers omitted from
`DISCORD_ROUTES` continue to use Pushover. If a Discord webhook is missing or a
send fails, that notification is logged and is not rerouted to Pushover.

## Usage

Run the program using:
```bash
python3 main.py
```

The program will:
1. Check availability for configured items
2. Process the results
3. Send notifications through Pushover or the configured Discord channel

## Project Structure

- `main.py` - Main program entry point
- `trackers/` - Directory containing individual item trackers
- `plists/` - macOS launch agent templates
- `service/pushover_service.py` - Handles default Pushover notifications
- `service/discord_service.py` - Handles Discord webhook notifications
- `util.py` - Utility functions
