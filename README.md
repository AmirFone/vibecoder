# Vibecoder

Text-to-app generator via iMessage. Send a text describing what you want, get back a working web app.

## How It Works

1. Send an iMessage to the Vibecoder number with `vibecode: [your idea]`
2. The message flows through Kafka to the server
3. An AI generates a complete HTML/CSS/JS app based on your description
4. You receive an SMS with a link to your creation

## Example

```
vibecode: a pac man game
```

Returns a fully playable Pac-Man game in your browser.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in your API keys

# Run
python main.py
```

## Environment Variables

- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker address
- `KAFKA_TOPIC` - Topic for incoming messages
- `ANTHROPIC_API_KEY` - API key for AI generation
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `TWILIO_PHONE_NUMBER` - Twilio phone number for sending SMS

## Architecture

```
iMessage → Kafka → Parser → AI Generator → HTTP Server → SMS Response
```

Built for the Series Hackathon 2025.
