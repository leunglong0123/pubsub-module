"""
PubSub Module
------------
A module for handling publish-subscribe messaging patterns.
"""

from .pubsub_base import PubSubBase
from .pubsub_publisher import PubSubPublisher

__all__ = [
    'PubSubBase',
    'PubSubPublisher',
]

__version__ = '0.1.0'

__doc_pubsub_base__ = """
PubSubBase: Base Class for Publish-Subscribe Pattern
-------------------------------------------------

A base class that implements the core functionality for publish-subscribe messaging.

Example usage:

>>> class MyPubSub(PubSubBase):
...     def __init__(self):
...         super().__init__()
...     def custom_publish(self, message):
...         self.publish("channel_name", message)

Basic Operations:

1. Subscribe to a channel:
   
>>> pubsub = MyPubSub()
>>> def my_callback(message):
...     print(f"Received: {message}")
>>> pubsub.subscribe("channel_name", my_callback)

2. Publish to a channel:

>>> pubsub.publish("channel_name", "Hello World!")
# Output: Received: Hello World!

3. Unsubscribe from a channel:

>>> pubsub.unsubscribe("channel_name", my_callback)

Multiple subscribers can listen to the same channel, and a single subscriber
can listen to multiple channels:

>>> def listener1(msg): print(f"Listener1: {msg}")
>>> def listener2(msg): print(f"Listener2: {msg}")
>>> pubsub.subscribe("channel1", listener1)
>>> pubsub.subscribe("channel1", listener2)
>>> pubsub.publish("channel1", "Broadcasting!")
# Output:
# Listener1: Broadcasting!
# Listener2: Broadcasting!

The PubSubBase class provides these core methods:

- subscribe(channel: str, callback: Callable): Subscribe to a channel
- unsubscribe(channel: str, callback: Callable): Unsubscribe from a channel
- publish(channel: str, message: Any): Publish a message to a channel
- get_subscribers(channel: str): Get all subscribers for a channel
- clear_subscribers(channel: str): Remove all subscribers from a channel

Thread Safety:
The implementation is thread-safe, using locks to protect shared resources
during subscribe/unsubscribe operations.

Error Handling:
- Raises ValueError for invalid channel names or callback functions
- Safely handles callback exceptions without affecting other subscribers
"""

__doc_pubsub_publisher__ = """
PubSubPublisher: Enhanced Publisher Implementation
----------------------------------------------

A concrete implementation of the publish-subscribe pattern, extending PubSubBase
with additional publishing capabilities and message handling features.

Example usage:

>>> publisher = PubSubPublisher()

1. Basic Publishing:

>>> def log_message(msg):
...     print(f"Received: {msg}")
>>> publisher.subscribe("notifications", log_message)
>>> publisher.publish("notifications", {"event": "user_login", "user_id": 123})
# Output: Received: {'event': 'user_login', 'user_id': 123}

2. Batch Publishing:

>>> messages = [
...     {"channel": "notifications", "message": "Message 1"},
...     {"channel": "alerts", "message": "Alert 1"}
... ]
>>> publisher.publish_batch(messages)

3. Async Publishing:

>>> await publisher.publish_async("notifications", "Async message")
>>> await publisher.publish_batch_async(messages)

4. Message Validation:

>>> # With schema validation enabled
>>> publisher.publish("user_events", {
...     "event_type": "registration",
...     "user_data": {"id": 1, "name": "John"}
... })  # Validates against schema before publishing

Features:

- Asynchronous Publishing: Support for async/await pattern
- Batch Operations: Efficient handling of multiple messages
- Schema Validation: Optional message validation against predefined schemas
- Error Recovery: Automatic retries for failed publish attempts
- Message Transformation: Pre-processing hooks for message modification

Configuration Options:

- schema_path: Path to JSON schema for message validation
- retry_attempts: Number of retry attempts for failed publishes
- async_timeout: Timeout for async operations
- batch_size: Maximum size for batch operations

Error Handling:

- Raises ValidationError for messages that don't match schema
- Raises PublishTimeoutError for async operations that exceed timeout
- Raises BatchSizeError for oversized batch operations

Thread Safety:
Inherits thread-safety features from PubSubBase and adds additional
synchronization for batch operations.

Performance Considerations:
- Batch operations are more efficient for high-volume publishing
- Async operations prevent blocking during I/O operations
- Schema validation adds overhead but ensures message integrity
"""

# Make the documentation accessible via help()
PubSubBase.__doc__ = __doc_pubsub_base__
PubSubPublisher.__doc__ = __doc_pubsub_publisher__
