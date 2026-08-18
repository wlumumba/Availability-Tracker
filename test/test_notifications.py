import os
import unittest
from unittest.mock import Mock, call, patch

import main
from service import discord_service


class NotificationRoutingTests(unittest.TestCase):
    def test_unconfigured_routes_use_pushover(self):
        data = {"sheridan": "available"}
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(main.pushover_service, "send_notifications") as pushover,
            patch.object(main.discord_service, "send_notifications") as discord,
        ):
            main.send_notifications(data)

        pushover.assert_called_once_with(data)
        discord.assert_not_called()

    def test_routes_group_by_channel_and_leave_defaults_on_pushover(self):
        data = {
            "hai_agora_track": "agora",
            "hai_ivy_track": "ivy",
            "sheridan": "apartment",
        }
        env = {
            "DISCORD_ROUTES": (
                "hai_agora_track=HAI_JOBS, hai_ivy_track=HAI_JOBS"
            ),
            "DISCORD_WEBHOOK_HAI_JOBS": "https://example.test/webhook",
        }
        with (
            patch.dict(os.environ, env, clear=True),
            patch.object(main.pushover_service, "send_notifications") as pushover,
            patch.object(main.discord_service, "send_notifications") as discord,
        ):
            main.send_notifications(data)

        pushover.assert_called_once_with({"sheridan": "apartment"})
        discord.assert_called_once_with(
            {"hai_agora_track": "agora", "hai_ivy_track": "ivy"},
            "https://example.test/webhook",
            "HAI_JOBS",
        )

    def test_missing_webhook_does_not_fall_back(self):
        data = {"hai_agora_track": "agora", "sheridan": "apartment"}
        with (
            patch.dict(
                os.environ,
                {"DISCORD_ROUTES": "hai_agora_track=HAI_JOBS"},
                clear=True,
            ),
            patch.object(main.pushover_service, "send_notifications") as pushover,
            patch.object(main.discord_service, "send_notifications") as discord,
        ):
            main.send_notifications(data)

        pushover.assert_called_once_with({"sheridan": "apartment"})
        discord.assert_not_called()

    def test_different_aliases_use_different_webhooks(self):
        data = {"hai_agora_track": "agora", "sheridan": "apartment"}
        env = {
            "DISCORD_ROUTES": "hai_agora_track=JOBS,sheridan=APARTMENTS",
            "DISCORD_WEBHOOK_JOBS": "https://example.test/jobs",
            "DISCORD_WEBHOOK_APARTMENTS": "https://example.test/apartments",
        }
        with (
            patch.dict(os.environ, env, clear=True),
            patch.object(main.pushover_service, "send_notifications") as pushover,
            patch.object(main.discord_service, "send_notifications") as discord,
        ):
            main.send_notifications(data)

        pushover.assert_not_called()
        self.assertEqual(
            discord.call_args_list,
            [
                call(
                    {"hai_agora_track": "agora"},
                    "https://example.test/jobs",
                    "JOBS",
                ),
                call(
                    {"sheridan": "apartment"},
                    "https://example.test/apartments",
                    "APARTMENTS",
                ),
            ],
        )

    def test_invalid_routes_are_rejected(self):
        invalid_routes = (
            "missing_separator",
            "sheridan=",
            "sheridan=lowercase",
            "unknown=CHANNEL",
            "sheridan=ONE,sheridan=TWO",
        )
        for routes in invalid_routes:
            with self.subTest(routes=routes), self.assertRaises(ValueError):
                main.parse_discord_routes(routes)

    def test_invalid_routes_stop_before_dispatch(self):
        with (
            patch.dict(os.environ, {"DISCORD_ROUTES": "unknown=CHANNEL"}, clear=True),
            patch.object(main.pushover_service, "send_notifications") as pushover,
            patch.object(main.discord_service, "send_notifications") as discord,
            self.assertRaises(ValueError),
        ):
            main.send_notifications({"sheridan": "available"})

        pushover.assert_not_called()
        discord.assert_not_called()


class DiscordServiceTests(unittest.TestCase):
    @patch.object(discord_service.requests, "post")
    def test_sends_safe_messages_and_splits_long_content(self, post):
        post.return_value = Mock()
        discord_service.send_notifications(
            {"sheridan": "@everyone " + "x" * 4000},
            "https://example.test/webhook",
            "APARTMENTS",
        )

        self.assertGreater(post.call_count, 1)
        for call in post.call_args_list:
            self.assertLessEqual(len(call.kwargs["json"]["content"]), 2000)
            self.assertEqual(call.kwargs["json"]["allowed_mentions"], {"parse": []})
            self.assertEqual(call.kwargs["params"], {"wait": "true"})
            self.assertEqual(call.kwargs["timeout"], 10)

    @patch.object(discord_service.requests, "post")
    def test_skips_empty_messages(self, post):
        discord_service.send_notifications(
            {"sheridan": "   ", "hai_agora_track": None},
            "https://example.test/webhook",
            "TEST",
        )
        post.assert_not_called()

    @patch.object(discord_service.requests, "post")
    def test_request_failure_is_contained(self, post):
        post.side_effect = discord_service.requests.RequestException("offline")
        discord_service.send_notifications(
            {"sheridan": "available"},
            "https://example.test/webhook",
            "TEST",
        )
        post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
