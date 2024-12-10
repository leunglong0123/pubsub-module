from pubsub_base import PubSubBase
import json
from typing import Any, Dict, Optional


class PubSubPublisher(PubSubBase):
    def __init__(self, project_id: str):
        """
        Initializes the Pub/Sub Publisher.
        :param project_id: Google Cloud Project ID
        """
        self.project_id = project_id
        self.base = PubSubBase(project_id)
        # Cache topic-specific publishers to avoid reinitialization

    def publish(
        self,
        topic_id: str,
        message: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Publishes a message to a Pub/Sub topic.
        :param topic_id: Pub/Sub topic name
        :param message: Message payload (must be JSON serializable)
        :param attributes: Optional key-value pairs as message attributes
        :return: Message ID of the published message
        """
        try:
            publisher = self._get_publisher(topic_id)
            topic_path = publisher.topic_path(self.project_id, topic_id)

            # Encode the message as JSON
            data = json.dumps(message).encode("utf-8")

            # Publish the message with optional attributes
            future = publisher.publish(topic_path, data, **(attributes or {}))

            # Return the message ID
            return future.result()
        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {e}")

    def close(self):
        """
        Closes all cached PublisherClient instances.
        """
        for publisher in self.publishers.values():
            publisher.transport.close()
