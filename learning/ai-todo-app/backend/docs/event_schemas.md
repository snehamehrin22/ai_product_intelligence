# Platform Event Schemas

This document describes all platform events emitted by the AI Todo App.

## Overview

All events inherit from the base `PlatformEvent` schema and include:
- `event_id` (string): Unique identifier (UUID v4)
- `event_name` (string): Event type identifier
- `event_version` (string): Schema version (default "v1")
- `timestamp` (string): Event occurrence time (ISO8601)
- `session_id` (string): User session identifier (join key)
- `user_id` (string): User identifier
- `properties` (dict): Event-specific data

## Event Types

### TaskCreatedEvent

**Description:** User creates a new task

**Event Name:** `task_created`

**Properties:**
- task_id (str): Unique task identifier
- title (str): Task title
- description (str, optional): Task description
- status (str): Initial task status (usually 'pending')
- priority (str, optional): Task priority level
- due_date (str, optional): Task due date (ISO8601)

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### TaskCompletedEvent

**Description:** User marks task as completed

**Event Name:** `task_completed`

**Properties:**
- task_id (str): Unique task identifier
- title (str): Task title
- completed_at (str): Completion timestamp (ISO8601)
- time_to_complete_seconds (int, optional): Time from creation to completion

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### TaskDeletedEvent

**Description:** User deletes a task

**Event Name:** `task_deleted`

**Properties:**
- task_id (str): Unique task identifier
- title (str): Task title
- status (str): Task status at deletion time

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### TaskUpdatedEvent

**Description:** User updates task fields

**Event Name:** `task_updated`

**Properties:**
- task_id (str): Unique task identifier
- title (str): Current task title
- updated_fields (list[str]): Names of fields that were updated
- previous_values (dict, optional): Previous values of updated fields
- current_values (dict): Current values of updated fields

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### PageViewedEvent

**Description:** User navigates to a page

**Event Name:** `page_viewed`

**Properties:**
- page_path (str): URL path or route (e.g., '/tasks', '/agent')
- page_title (str, optional): Page title
- referrer (str, optional): Previous page URL

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### AgentMessageSentEvent

**Description:** User sends message to AI agent

**Event Name:** `agent_message_sent`

**Properties:**
- message_id (str): Unique message identifier
- message_text (str): User's message content
- message_length (int): Character count
- conversation_id (str, optional): Conversation thread identifier

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### AgentMessageReceivedEvent

**Description:** AI agent responds to user

**Event Name:** `agent_message_received`

**Properties:**
- message_id (str): Unique message identifier
- response_text (str): Agent's response content
- response_length (int): Character count
- conversation_id (str, optional): Conversation thread identifier
- user_message_id (str, optional): ID of user message being responded to
- response_time_ms (int, optional): Time to generate response in milliseconds

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

### SessionStartedEvent

**Description:** User session begins

**Event Name:** `session_started`

**Properties:**
- user_agent (str, optional): Browser user agent string
- screen_width (int, optional): Browser screen width in pixels
- screen_height (int, optional): Browser screen height in pixels
- timezone (str, optional): User's timezone (e.g., 'America/Los_Angeles')
- language (str, optional): Browser language (e.g., 'en-US')

**Example:**
```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_name": "task_created",
  "event_version": "v1",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "session_id": "abc-123-session",
  "user_id": "user-456",
  "properties": {
    "task_id": "task-789",
    "title": "Buy milk"
  }
}
```

---

