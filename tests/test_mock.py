from unittest.mock import Mock

api = Mock()

api.get_events.side_effect = ["Austin", "Chicago"]

print(api.get_events())
print(api.get_events())