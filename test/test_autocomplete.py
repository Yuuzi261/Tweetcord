import os
import sys
import tempfile
import sqlite3
import unittest
from types import SimpleNamespace, ModuleType
from unittest.mock import MagicMock, patch, AsyncMock

import yaml
import discord
from discord import app_commands

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs.constants import AUTOCOMPLETE_MAX_CHOICES, AUTOCOMPLETE_MAX_CHOICE_LENGTH

# Stub config/env-dependent modules before importing cogs so the test suite works
# on a clean checkout without generated config files or a local TWITTER_TOKEN.

if 'configs.load_configs' not in sys.modules:
    _example_cfg_path = os.path.join(os.path.dirname(__file__), '..', 'configs.example.yml')
    with open(_example_cfg_path, 'r', encoding='utf-8') as _f:
        _fake_configs = yaml.safe_load(_f)

    _fake_mod = ModuleType('configs.load_configs')
    _fake_mod.configs = _fake_configs
    _fake_mod.FX_SETTINGS = _fake_configs['embed']['built_in']['fx']
    _fake_mod.IS_TRANSLATION_ENABLED = (
        _fake_mod.FX_SETTINGS['auto_translation']
        if _fake_configs['embed']['type'] == 'built_in'
        else _fake_configs['embed']['proxy']['auto_translation']
    )
    sys.modules['configs.load_configs'] = _fake_mod

# init_i18n only reads locales/en.yml (tracked in git) — no config / env dependency.
from src.i18n import init_i18n
init_i18n()

# Monkey-patch get_accounts before the Notification class body evaluates it.
import src.utils
src.utils.get_accounts = lambda: {'test_account': 'fake_token'}

from src.discord_ui.fetch_tracked_channels import fetch_tracked_channels
from cogs.list_users import ListUsers
from cogs.notification import Notification


def create_test_db(db_path: str):
    """Creates the SQLite schema required for testing autocomplete queries."""
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            username TEXT,
            latest_tweet TEXT,
            client_used TEXT,
            enabled INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS channel (
            id TEXT PRIMARY KEY,
            server_id TEXT
        );
        CREATE TABLE IF NOT EXISTS notification (
            user_id TEXT,
            channel_id TEXT,
            role_id TEXT,
            enabled INTEGER DEFAULT 1,
            enable_type TEXT DEFAULT '11',
            enable_media_type TEXT DEFAULT '11',
            customized_msg TEXT DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (channel_id) REFERENCES channel (id),
            PRIMARY KEY(user_id, channel_id)
        );
    """)
    conn.commit()
    conn.close()


def assert_discord_autocomplete_compliant(test_case: unittest.TestCase, choices: list[app_commands.Choice], check_value: bool = True):
    """Validates that autocomplete choices strictly adhere to Discord API constraints.

    Discord constraints:
    - Choices count <= 25 (exceeding causes HTTP 400 Bad Request error code 50035, Issue #98)
    - Choice name length between 1 and 100 characters (Commit c4d0321, Issue #98)
    - Choice value length <= 100 characters (if check_value is True)
    """
    test_case.assertLessEqual(
        len(choices),
        AUTOCOMPLETE_MAX_CHOICES,
        f"Discord API limit violated: returned {len(choices)} choices, maximum allowed is {AUTOCOMPLETE_MAX_CHOICES}."
    )
    for i, choice in enumerate(choices):
        test_case.assertIsInstance(choice, app_commands.Choice)
        test_case.assertGreater(
            len(choice.name),
            0,
            f"Choice [{i}] name must not be empty."
        )
        test_case.assertLessEqual(
            len(choice.name),
            AUTOCOMPLETE_MAX_CHOICE_LENGTH,
            f"Discord API limit violated: Choice [{i}] name '{choice.name}' has {len(choice.name)} characters, max is {AUTOCOMPLETE_MAX_CHOICE_LENGTH}."
        )
        if check_value and isinstance(choice.value, str):
            test_case.assertLessEqual(
                len(choice.value),
                AUTOCOMPLETE_MAX_CHOICE_LENGTH,
                f"Choice [{i}] value '{choice.value}' exceeds {AUTOCOMPLETE_MAX_CHOICE_LENGTH} characters."
            )


class TestFetchTrackedChannels(unittest.IsolatedAsyncioTestCase):
    """Tests for fetch_tracked_channels covering commits c4d0321, 6ac6357, and issues #52, #98."""

    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'tracked_accounts.db')
        create_test_db(self.db_path)
        self.env_patch = patch.dict(os.environ, {'DATA_PATH': self.temp_dir.name})
        self.env_patch.start()

        self.itn = MagicMock(spec=discord.Interaction)
        self.itn.guild_id = 123456789
        self.itn.guild = MagicMock()

    async def asyncTearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    async def test_max_choices_limit_25_issue_98(self):
        """Simulate high channel count (Issue #98): choices must never exceed 25."""
        conn = sqlite3.connect(self.db_path)
        # Insert 60 channels for this server, each with active notification
        for i in range(60):
            cid = f'{1000 + i}'
            conn.execute('INSERT INTO channel VALUES (?, ?)', (cid, str(self.itn.guild_id)))
            conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', (f'u_{i}', cid))
        conn.commit()
        conn.close()

        def make_channel(cid):
            ch = MagicMock(spec=discord.TextChannel)
            ch.name = f'channel-{cid}'
            return ch

        self.itn.guild.get_channel_or_thread.side_effect = make_channel

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)

    async def test_early_break_performance_commit_6ac6357(self):
        """Verify performance optimization from commit 6ac6357: breaks early once 25 items are reached."""
        conn = sqlite3.connect(self.db_path)
        # Insert 50 channels
        for i in range(50):
            cid = f'{2000 + i}'
            conn.execute('INSERT INTO channel VALUES (?, ?)', (cid, str(self.itn.guild_id)))
            conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', (f'u_{i}', cid))
        conn.commit()
        conn.close()

        def make_channel(cid):
            ch = MagicMock(spec=discord.TextChannel)
            ch.name = f'ch-{cid}'
            return ch

        self.itn.guild.get_channel_or_thread.side_effect = make_channel

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)
        # get_channel_or_thread must only be called 25 times due to early break
        self.assertEqual(self.itn.guild.get_channel_or_thread.call_count, AUTOCOMPLETE_MAX_CHOICES)

    async def test_text_channel_name_truncation_to_100_chars_issue_98_commit_c4d0321(self):
        """100-character channel name + '# ' prefix (102 chars) must be truncated to <= 100 chars."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('3001', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_long', '3001'))
        conn.commit()
        conn.close()

        max_len_name = 'x' * AUTOCOMPLETE_MAX_CHOICE_LENGTH
        ch = MagicMock(spec=discord.TextChannel)
        ch.name = max_len_name
        self.itn.guild.get_channel_or_thread.return_value = ch

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), 1)
        self.assertEqual(len(choices[0].name), AUTOCOMPLETE_MAX_CHOICE_LENGTH)
        self.assertTrue(choices[0].name.startswith('# '))
        self.assertEqual(choices[0].value, '3001')

    async def test_thread_name_truncation_to_100_chars_issue_98_commit_c4d0321(self):
        """100-character thread name + '🧵 ' prefix must be truncated to <= 100 chars."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('3002', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_thread', '3002'))
        conn.commit()
        conn.close()

        max_len_thread_name = 'y' * AUTOCOMPLETE_MAX_CHOICE_LENGTH
        th = MagicMock(spec=discord.Thread)
        th.name = max_len_thread_name
        self.itn.guild.get_channel_or_thread.return_value = th

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), 1)
        self.assertEqual(len(choices[0].name), AUTOCOMPLETE_MAX_CHOICE_LENGTH)
        self.assertTrue(choices[0].name.startswith('🧵 '))
        self.assertEqual(choices[0].value, '3002')

    async def test_text_channel_and_thread_prefixes(self):
        """TextChannel should use '# ' prefix, Thread should use '🧵 ' prefix."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('4001', str(self.itn.guild_id)))
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('4002', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u1', '4001'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u2', '4002'))
        conn.commit()
        conn.close()

        ch = MagicMock(spec=discord.TextChannel)
        ch.name = 'text-updates'
        th = MagicMock(spec=discord.Thread)
        th.name = 'thread-updates'

        self.itn.guild.get_channel_or_thread.side_effect = lambda cid: ch if cid == 4001 else th

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        choice_dict = {c.value: c.name for c in choices}
        self.assertEqual(choice_dict['4001'], '# text-updates')
        self.assertEqual(choice_dict['4002'], '🧵 thread-updates')

    async def test_deleted_channel_included_when_include_unknown_true_issue_52(self):
        """Issue #52: Deleted channels appear as '# unknown ({channel_id})' when include_unknown=True."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('5001', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_del', '5001'))
        conn.commit()
        conn.close()

        # get_channel_or_thread returns None for deleted channels
        self.itn.guild.get_channel_or_thread.return_value = None

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].name, '# unknown (5001)')
        self.assertEqual(choices[0].value, '5001')

    async def test_deleted_channel_excluded_when_include_unknown_false_issue_52(self):
        """Issue #52: Deleted channels must NOT appear when include_unknown=False (e.g. /customize settings)."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('5002', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_del', '5002'))
        conn.commit()
        conn.close()

        self.itn.guild.get_channel_or_thread.return_value = None

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=False)
        self.assertEqual(choices, [])

    async def test_filter_by_input_channel_case_insensitive_and_hash_stripping(self):
        """User input matching should be case-insensitive and ignore leading '# '."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('6001', str(self.itn.guild_id)))
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('6002', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u1', '6001'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u2', '6002'))
        conn.commit()
        conn.close()

        ch1 = MagicMock(spec=discord.TextChannel)
        ch1.name = 'General-Chat'
        ch2 = MagicMock(spec=discord.TextChannel)
        ch2.name = 'announcements'

        self.itn.guild.get_channel_or_thread.side_effect = lambda cid: ch1 if cid == 6001 else ch2

        # Filter with uppercase
        choices = await fetch_tracked_channels(self.itn, 'GENERAL', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '6001')

        # Filter with leading '#'
        choices = await fetch_tracked_channels(self.itn, '#general', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '6001')

        # Filter with substring
        choices = await fetch_tracked_channels(self.itn, 'announce', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '6002')

    async def test_search_deleted_channel_by_keyword_or_id_issue_52(self):
        """Deleted channel can be searched using 'unknown' or its channel ID."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('998877', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_del', '998877'))
        conn.commit()
        conn.close()

        self.itn.guild.get_channel_or_thread.return_value = None

        # Searching 'unknown' matches
        choices = await fetch_tracked_channels(self.itn, 'unknown', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '998877')

        # Searching channel ID matches
        choices = await fetch_tracked_channels(self.itn, '9988', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '998877')

        # Non-matching keyword returns empty
        choices = await fetch_tracked_channels(self.itn, 'random', include_unknown=True)
        self.assertEqual(len(choices), 0)

    async def test_ignores_channels_without_active_notifications(self):
        """Channels with no notifications or only disabled (enabled = 0) notifications are excluded."""
        conn = sqlite3.connect(self.db_path)
        # Channel 7001 has no notifications
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('7001', str(self.itn.guild_id)))
        # Channel 7002 has only disabled notifications
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('7002', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 0)', ('u_disabled', '7002'))
        # Channel 7003 has an active notification
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('7003', str(self.itn.guild_id)))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u_active', '7003'))
        conn.commit()
        conn.close()

        ch = MagicMock(spec=discord.TextChannel)
        ch.name = 'active-channel'
        self.itn.guild.get_channel_or_thread.return_value = ch

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, '7003')

    async def test_ignores_channels_from_other_guilds(self):
        """Channels belonging to other guilds must not be returned."""
        conn = sqlite3.connect(self.db_path)
        other_guild_id = '999999999'
        conn.execute('INSERT INTO channel VALUES (?, ?)', ('8001', other_guild_id))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u1', '8001'))
        conn.commit()
        conn.close()

        ch = MagicMock(spec=discord.TextChannel)
        ch.name = 'other-guild-chan'
        self.itn.guild.get_channel_or_thread.return_value = ch

        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        self.assertEqual(choices, [])


class TestListUsersAutocomplete(unittest.IsolatedAsyncioTestCase):
    """Tests for cogs/list_users.py autocomplete methods (account & channel)."""

    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'tracked_accounts.db')
        create_test_db(self.db_path)
        self.env_patch = patch.dict(os.environ, {'DATA_PATH': self.temp_dir.name})
        self.env_patch.start()

        self.cog = ListUsers.__new__(ListUsers)
        self.cog.bot = MagicMock()
        self.itn = MagicMock(spec=discord.Interaction)
        self.itn.guild_id = 123456789

    async def asyncTearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    async def test_get_clients_max_choices_limit_25_issue_98_commit_c4d0321(self):
        """get_clients must return at most 25 choices when > 25 clients exist in DB."""
        conn = sqlite3.connect(self.db_path)
        for i in range(35):
            conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)',
                         (str(i), f'user_{i}', f'client_token_{i:02d}'))
        conn.commit()
        conn.close()

        choices = await self.cog.get_clients(self.itn, '')
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)

    async def test_get_clients_choice_name_truncation_commit_c4d0321(self):
        """When client_used exceeds 100 characters, choice.name is truncated to 100 chars, value is intact."""
        long_client = 'ClientAccount_' + 'z' * 120
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)',
                     ('u_long', 'user_long', long_client))
        conn.commit()
        conn.close()

        choices = await self.cog.get_clients(self.itn, 'ClientAccount')
        assert_discord_autocomplete_compliant(self, choices, check_value=False)
        self.assertEqual(len(choices), 1)
        self.assertEqual(len(choices[0].name), AUTOCOMPLETE_MAX_CHOICE_LENGTH)
        self.assertEqual(choices[0].value, long_client)

    async def test_get_clients_filtering_case_insensitive(self):
        """Filtering by account argument is case-insensitive."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)', ('1', 'u1', 'AlphaClient'))
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)', ('2', 'u2', 'BetaClient'))
        conn.commit()
        conn.close()

        choices = await self.cog.get_clients(self.itn, 'alpha')
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, 'AlphaClient')

    async def test_get_clients_ignores_disabled_users(self):
        """Users with enabled = 0 are ignored in get_clients."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 0)', ('1', 'u1', 'InactiveClient'))
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)', ('2', 'u2', 'ActiveClient'))
        conn.commit()
        conn.close()

        choices = await self.cog.get_clients(self.itn, '')
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, 'ActiveClient')

    async def test_get_clients_deduplicates_clients(self):
        """Multiple users sharing the same client_used produce only one choice."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)', ('1', 'u1', 'SharedClient'))
        conn.execute('INSERT INTO user (id, username, client_used, enabled) VALUES (?, ?, ?, 1)', ('2', 'u2', 'SharedClient'))
        conn.commit()
        conn.close()

        choices = await self.cog.get_clients(self.itn, '')
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].value, 'SharedClient')

    @patch('cogs.list_users.fetch_tracked_channels', new_callable=AsyncMock)
    async def test_get_channel_delegates_with_include_unknown_true_issue_52(self, mock_fetch):
        """list_users.get_channel must call fetch_tracked_channels with include_unknown=True."""
        mock_fetch.return_value = [app_commands.Choice(name='# general', value='1001')]
        result = await self.cog.get_channel(self.itn, 'gen')

        mock_fetch.assert_awaited_once_with(self.itn, 'gen', include_unknown=True)
        self.assertEqual(result, mock_fetch.return_value)


class TestNotificationAutocomplete(unittest.IsolatedAsyncioTestCase):
    """Tests for cogs/notification.py autocomplete methods."""

    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'tracked_accounts.db')
        create_test_db(self.db_path)
        self.env_patch = patch.dict(os.environ, {'DATA_PATH': self.temp_dir.name})
        self.env_patch.start()

        self.cog = Notification.__new__(Notification)
        self.cog.bot = MagicMock()
        self.itn = MagicMock(spec=discord.Interaction)
        self.itn.guild_id = 123456789

    async def asyncTearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    @patch('cogs.notification.fetch_tracked_channels', new_callable=AsyncMock)
    async def test_r_notifier_channel_delegates_with_include_unknown_true_issue_52(self, mock_fetch):
        """/remove notifier channel autocomplete must pass include_unknown=True to allow deleting dead channels."""
        mock_fetch.return_value = [app_commands.Choice(name='# unknown (1001)', value='1001')]
        result = await self.cog.get_channels_for_r_notifier(self.itn, 'unknown')

        mock_fetch.assert_awaited_once_with(self.itn, 'unknown', include_unknown=True)
        self.assertEqual(result, mock_fetch.return_value)

    @patch('cogs.notification.fetch_tracked_channels', new_callable=AsyncMock)
    async def test_customize_settings_channel_delegates_with_include_unknown_false_issue_52(self, mock_fetch):
        """/customize settings channel autocomplete must pass include_unknown=False to prevent configuring dead channels."""
        mock_fetch.return_value = [app_commands.Choice(name='# general', value='1002')]
        result = await self.cog.get_channels_for_customize_message(self.itn, 'general')

        mock_fetch.assert_awaited_once_with(self.itn, 'general', include_unknown=False)
        self.assertEqual(result, mock_fetch.return_value)

    async def test_get_enabled_users_no_channel_selected_returns_empty_commit_8ac89f0(self):
        """Commit 8ac89f0: when namespace.channel is None or unset, returns [] immediately."""
        self.itn.namespace = SimpleNamespace()
        result = await self.cog.get_enabled_users(self.itn, '')
        self.assertEqual(result, [])

        self.itn.namespace = SimpleNamespace(channel=None)
        result2 = await self.cog.get_enabled_users(self.itn, '')
        self.assertEqual(result2, [])

    async def test_get_enabled_users_max_choices_limit_25_issue_98_commit_c4d0321(self):
        """get_enabled_users must return at most 25 choices when > 25 users are tracked in channel."""
        channel_id = '9001'
        self.itn.namespace = SimpleNamespace(channel=channel_id)

        conn = sqlite3.connect(self.db_path)
        for i in range(35):
            uid = f'user_id_{i}'
            uname = f'twitter_user_{i:02d}'
            conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', (uid, uname))
            conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', (uid, channel_id))
        conn.commit()
        conn.close()

        choices = await self.cog.get_enabled_users(self.itn, '')
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)

    async def test_get_enabled_users_filtering_and_channel_isolation(self):
        """get_enabled_users filters by username case-insensitively and isolates to the selected channel."""
        target_channel = '9002'
        other_channel = '9003'
        self.itn.namespace = SimpleNamespace(channel=target_channel)

        conn = sqlite3.connect(self.db_path)
        # Users in target channel
        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('u1', 'elonmusk'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u1', target_channel))

        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('u2', 'billgates'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u2', target_channel))

        # Disabled notification in target channel
        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('u3', 'jeffbezos'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 0)', ('u3', target_channel))

        # User in other channel
        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('u4', 'satyanadella'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('u4', other_channel))

        conn.commit()
        conn.close()

        # Case-insensitive match on 'ELON'
        choices = await self.cog.get_enabled_users(self.itn, 'ELON')
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].name, 'elonmusk')
        self.assertEqual(choices[0].value, 'elonmusk')

        # Empty search returns all enabled in target channel (u1, u2), excludes disabled (u3) and other channel (u4)
        all_choices = await self.cog.get_enabled_users(self.itn, '')
        names = {c.name for c in all_choices}
        self.assertEqual(names, {'elonmusk', 'billgates'})

    async def test_get_guild_enabled_users_max_choices_limit_25_issue_98_commit_c4d0321(self):
        """get_guild_enabled_users must return at most 25 choices when > 25 users are tracked in guild."""
        conn = sqlite3.connect(self.db_path)
        channel_id = '9010'
        conn.execute('INSERT INTO channel VALUES (?, ?)', (channel_id, str(self.itn.guild_id)))
        for i in range(40):
            uid = f'guid_{i}'
            uname = f'guild_user_{i:02d}'
            conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', (uid, uname))
            conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', (uid, channel_id))
        conn.commit()
        conn.close()

        choices = await self.cog.get_guild_enabled_users(self.itn, '')
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)

    async def test_get_guild_enabled_users_filtering_and_guild_isolation(self):
        """get_guild_enabled_users filters by username case-insensitively and isolates to the current guild."""
        my_guild_channel = '9020'
        other_guild_channel = '9021'

        conn = sqlite3.connect(self.db_path)
        conn.execute('INSERT INTO channel VALUES (?, ?)', (my_guild_channel, str(self.itn.guild_id)))
        conn.execute('INSERT INTO channel VALUES (?, ?)', (other_guild_channel, '999999999'))

        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('g1', 'nasa'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('g1', my_guild_channel))

        conn.execute('INSERT INTO user (id, username, enabled) VALUES (?, ?, 1)', ('g2', 'esa'))
        conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', ('g2', other_guild_channel))

        conn.commit()
        conn.close()

        choices = await self.cog.get_guild_enabled_users(self.itn, 'NASA')
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].name, 'nasa')

        # ESA belongs to another guild, must not appear
        all_choices = await self.cog.get_guild_enabled_users(self.itn, '')
        names = {c.name for c in all_choices}
        self.assertEqual(names, {'nasa'})


class TestDiscordApiLimitsSimulation(unittest.IsolatedAsyncioTestCase):
    """Stress testing edge cases from Issue #98 (400+ channels, long names) against Discord constraints."""

    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'tracked_accounts.db')
        create_test_db(self.db_path)
        self.env_patch = patch.dict(os.environ, {'DATA_PATH': self.temp_dir.name})
        self.env_patch.start()

        self.itn = MagicMock(spec=discord.Interaction)
        self.itn.guild_id = 987654321
        self.itn.guild = MagicMock()

    async def asyncTearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    async def test_simulate_400_plus_channels_and_long_names(self):
        """Simulate Issue #98: server with 400+ channels and very long channel names.

        Discord will reject with HTTP 400 if:
        1. choices length > 25
        2. any choice.name length > 100
        """
        conn = sqlite3.connect(self.db_path)
        # Insert 450 channels with notifications
        for i in range(450):
            cid = str(10000 + i)
            conn.execute('INSERT INTO channel VALUES (?, ?)', (cid, str(self.itn.guild_id)))
            conn.execute('INSERT INTO notification (user_id, channel_id, enabled) VALUES (?, ?, 1)', (f'u_{i}', cid))
        conn.commit()
        conn.close()

        def make_channel(cid):
            idx = cid - 10000
            if idx % 3 == 0:
                # TextChannel with 100 characters (max Discord name)
                ch = MagicMock(spec=discord.TextChannel)
                ch.name = f'tc-{idx:03d}-' + 't' * 90
                return ch
            elif idx % 3 == 1:
                # Thread with 100 characters
                th = MagicMock(spec=discord.Thread)
                th.name = f'th-{idx:03d}-' + 'h' * 90
                return th
            else:
                # Deleted channel (Issue #52)
                return None

        self.itn.guild.get_channel_or_thread.side_effect = make_channel

        # Test empty input: should return 25 choices, every choice complying with Discord limits
        choices = await fetch_tracked_channels(self.itn, '', include_unknown=True)
        assert_discord_autocomplete_compliant(self, choices)
        self.assertEqual(len(choices), AUTOCOMPLETE_MAX_CHOICES)

        # Test filtering by thread: should return 25 choices, all complying
        th_choices = await fetch_tracked_channels(self.itn, 'th-', include_unknown=True)
        assert_discord_autocomplete_compliant(self, th_choices)
        self.assertEqual(len(th_choices), AUTOCOMPLETE_MAX_CHOICES)
        for c in th_choices:
            self.assertTrue(c.name.startswith('🧵 '))

        # Test filtering by unknown: should return deleted channels up to 25
        del_choices = await fetch_tracked_channels(self.itn, 'unknown', include_unknown=True)
        assert_discord_autocomplete_compliant(self, del_choices)
        self.assertGreater(len(del_choices), 0)
        self.assertLessEqual(len(del_choices), AUTOCOMPLETE_MAX_CHOICES)
        for c in del_choices:
            self.assertTrue(c.name.startswith('# unknown ('))


if __name__ == '__main__':
    unittest.main()
