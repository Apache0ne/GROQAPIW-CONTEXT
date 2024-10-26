import uuid
import json
import os
import logging
from collections import OrderedDict
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChatHistoryManager:
    def __init__(self, history_file="GROQ_CONTEXT.json"):
        self.history_file = self.get_history_file_path(history_file)
        logger.debug(f"Initializing ChatHistoryManager with file: {self.history_file}")
        self.ensure_valid_file()

    def get_history_file_path(self, filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Starting directory: {current_dir}")

        while os.path.basename(current_dir) != 'ComfyUI-GroqChatNodeFull':
            current_dir = os.path.dirname(current_dir)
            logger.debug(f"Moving up to: {current_dir}")
            if current_dir == os.path.dirname(current_dir):
                raise FileNotFoundError("Could not find 'ComfyUI-GroqChatNodeFull' directory")

        json_path = os.path.join(current_dir, 'nodes', 'groq', filename)
        logger.debug(f"Constructed JSON path: {json_path}")

        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        return json_path

    def ensure_valid_file(self):
        if not os.path.exists(self.history_file):
            logger.debug(f"Creating new history file: {self.history_file}")
            with open(self.history_file, 'w') as f:
                json.dump({}, f)

    def load_history(self):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with open(self.history_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return OrderedDict(json.loads(content))
                    else:
                        logger.warning("History file is empty")
                        return OrderedDict()
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(0.1)  # Short delay before retry
            except Exception as e:
                logger.error(f"Unexpected error loading history (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(0.1)  # Short delay before retry
        logger.error("Failed to load history after multiple attempts")
        return OrderedDict()

    def save_history(self, conversations):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with open(self.history_file, 'w') as f:
                    json.dump(conversations, f, indent=2)
                logger.debug(f"History saved successfully. Total conversations: {len(conversations)}")
                return
            except Exception as e:
                logger.error(f"Error saving history (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(0.1)  # Short delay before retry
        logger.error("Failed to save history after multiple attempts")

    def create_new_conversation(self):
        conversations = self.load_history()
        conversation_id = str(uuid.uuid4())
        conversations[conversation_id] = []
        self.save_history(conversations)
        return conversation_id

    def get_history(self, conversation_id):
        conversations = self.load_history()
        return conversations.get(conversation_id, [])

    def update_history(self, conversation_id, messages):
        conversations = self.load_history()
        conversations[conversation_id] = messages
        self.save_history(conversations)

    def get_all_conversations(self):
        return self.load_history()