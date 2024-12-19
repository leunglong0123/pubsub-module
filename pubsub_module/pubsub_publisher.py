from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding
from google.api_core.exceptions import NotFound

from datetime import datetime
import uuid
import avro.schema
import avro.io
import io
import json
from typing import Any, Dict, List, Optional
from pubsub_module.pubsub_base import PubSubBase


SPEC_VERSION = "1.0.0"


class PubSubPublisher(PubSubBase):
    def __init__(self, project_id: str, avsc_file: str, event_type: str = "default-event-type", event_source: str = "default.event.source", correlation_id: str = 'default-pubsub-class', metadata_tags: List[str] = None):
        """
        Initializes the Pub/Sub Publisher.
        :param project_id: Google Cloud Project ID
        :param avsc_file: Path to the Avro schema file
        """
        self.project_id = project_id
        self.event_type = event_type
        self.source = event_source
        self.correlation_id = correlation_id
        self.spec_version = SPEC_VERSION  # Fixed constant specVersion
        self.base = PubSubBase(project_id)
        self.avsc_file = avsc_file
        self.tags = metadata_tags

        # Load Avro schema
        with open(avsc_file, "rb") as f:
            self.avro_schema = avro.schema.parse(f.read())

        # Cache topic-specific publishers to avoid reinitialization
        self.publisher_client = PublisherClient()
        super().__init__(project_id)

    def _generate_event_context(self, trace_id: str) -> Dict[str, Any]:
        """
        Generates the event context, filling in dynamic fields.

        :param trace_id: Trace ID for the message.
        :return: The event context dictionary.
        """
        return {
            "eventId": str(uuid.uuid4()),  # Dynamically generate eventId
            "eventType": self.event_type,  # Fixed eventType
            # Generate event timestamp
            "eventTimestamp": datetime.now(datetime.UTC),
            "source": self.source,  # Fixed source
            "specVersion": self.spec_version,  # Fixed specVersion
            "correlationId": {"string": self.correlation_id},
            "traceId": {"string": trace_id}  # Trace ID passed as an argument
        }

    def publish(
        self,
        topic_id: str,
        message: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None,
        trace_id: str = None
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

            # Fetch the topic's schema settings to determine the encoding
            topic = self.publisher_client.get_topic(
                request={"topic": topic_path})
            encoding = topic.schema_settings.encoding

            message["eventContext"] = self._generate_event_context(trace_id)
            message["payload"]["metadata"] = {
                "EventPayloadMetadata": {
                    "version": {"string": "1.0.0"},
                    "tags": self.tags
                }
            }

            # Encode the message using Avro
            if encoding == Encoding.BINARY:
                # Binary encoding
                data = self._encode_avro_binary(message)
                print("Preparing a binary-encoded Avro message...")
            elif encoding == Encoding.JSON:
                # JSON encoding
                data = self._encode_avro_json(message)
                print("Preparing a JSON-encoded Avro message...")
            else:
                raise ValueError(f"Unsupported encoding type: {encoding}")

            future = publisher.publish(topic_path, data)
            res = future.result()
            return res
        except NotFound:
            raise RuntimeError(f"Topic {topic_id} not found.")
        except Exception as e:
            raise RuntimeError(f"Failed to publish message: {e}")

    def _encode_avro_binary(self, record: Dict[str, Any]) -> bytes:
        """
        Encodes the record using Avro's binary encoding.
        :param record: Record to be encoded
        :return: Encoded Avro binary data
        """
        writer = avro.io.DatumWriter(self.avro_schema)
        bout = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bout)
        writer.write(record, encoder)
        return bout.getvalue()

    def _encode_avro_json(self, record: Dict[str, Any]) -> bytes:
        """
        Encodes the record using Avro's JSON encoding.
        :param record: Record to be encoded
        :return: Encoded Avro JSON data
        """
        # For Avro JSON encoding, we can directly convert the record to JSON
        return json.dumps(record).encode("utf-8")

    def close(self):
        """
        Closes all cached PublisherClient instances.
        """
        for publisher in self.publishers.values():
            publisher.transport.close()
