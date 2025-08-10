# Changelog

## 0.6 (August 10, 2025)

**✨Features:**
- Renamed `fx_twitter` to `proxy` in the configuration and added support for multiple proxy services.
- Added a global setting for translation language with FxTwitter (resolves issue [#57](https://github.com/Yuuzi261/Tweetcord/issues/57)).

**♻️Refactor:** 
- Conducted a major refactoring of the notification system (`AccountTracker`) to resolve critical performance bottlenecks under high load (issue [#59](https://github.com/Yuuzi261/Tweetcord/issues/59)). This includes centralizing database operations, using a producer-consumer pattern for database writes, and optimizing database connection handling.
- Improved the task monitor to dynamically track tasks from a live cache, eliminating the need to restart the monitor when tasks are added or removed.
- Improved and simplified the handling of configuration files.

**🐛Fixes:**
- Resolved a critical issue where calls to the `tweety-ns` library could perform synchronous, CPU-intensive operations, leading to `heartbeat blocked` errors. These calls are now safely isolated in a separate thread.
- Added specific error handling for `KeyError` during tweet fetching, preventing task crashes due to temporary or unexpected API responses from Twitter.

## 0.5.5 (July 11, 2025)
**🐛Fix:**
- Fixed issue [#55](https://github.com/Yuuzi261/Tweetcord/issues/55)(Failed to re-add users with different casing due to a `UNIQUE constraint failed` error after deletion).

## 0.5.4 (May 4, 2025)
**✨Features:**
- Removed unnecessary Discord intents, resulting in a lighter startup and reduced system resource usage.
- Supported short emoji format in custom messages.
- Added a video link button for built-in embeds and an original URL button for FxTwitter.
- Customize message command now also supports auto-completion.
- Allowed free choice of a built-in embed footer, which can be the legacy bluebird logo or the new X logo.

**🐛Fix:**
- Fixed the incorrect task closure logic (High impact issue).
- Resolved autocomplete failure for deleted channels.
- Channels without any notifier will no longer be added to autocomplete.
- Ensured error messages are ephemeral.

## 0.5.3 (December 19, 2024)  
**✨Features:**  
- Enhanced **list users** command with pagination switchable via buttons.   
- Real-time updating of the number of tracked accounts.   
- Customizable page counter position and page size.   
- Ability to specify which domain (`fxtwitter` or `fixupx`) to use in the configuration.   
- Error logging when a notification fails to send.   
- Added handling for login failures.   

**♻️Refactor:**  
- Optimized database operations by adding locks to avoid conflicts during simultaneous writes.   
- Switched database connections to read-only mode when no writes are required.   
- Replaced deprecated `datetime.utcnow()` calls with updated alternatives.  
- Consolidated authentication to log in once per session instead of repeatedly using `auth_token`.

**🐛Fix:**  
- Added missing parameter checks in the configuration checker.   

## 0.5.2 (November 26, 2024)  
**♻️Refactor:**  
- Updated operations related to the `tweety-ns` library to use coroutines, addressing compatibility with its version update. 

## 0.5.1 (September 17, 2024)  
**✨Features:**  
- Media-type filtering in settings, allowing users to choose whether to forward images and/or videos. 
- Support for built-in multiple embedded images, with optional replacement by fx combined images. 
- Multi-client support: add multiple tokens and map which account follows which user. 
- Autocomplete for select slash commands. 
- Customizable bot activity type and message content. 
- Split listing to prevent cutoff of long outputs. 
- Optimized the update process for better performance. 
- Added startup checks for environment variables, configurations, and database. 

**♻️Refactor:**  
- Converted all SQL operations to asynchronous functions to avoid blocking. 
- General code optimizations and cleanup. 

**🎉New Contributors:**
- @Neppu-Nep made their first contribution in [#31](https://github.com/Yuuzi261/Tweetcord/pull/31)

## 0.4.1 (July 31, 2024)  
**✨Features:**  
- Ability to filter notifications by action type (e.g., send only tweets and retweets, exclude quote tweets). 
- Support for FxTwitter URL replacement in embedded content. 
- Default message templates can now be defined in the configuration. 

**🎉New Contributors:**
- @FuseFairy made their first contribution

## 0.4-hotfix (January 25, 2024)  
**✨Features:**  
- Custom notification messages per server, enabling tailored alerts. 
- Automatic disabling of tasks when all notifications for an account are removed. 
- Option to disable notifications or unfollow a Twitter account after removing all its notifiers. 
- New permission-checking method: default to administrators, with per-server overrides. 
- `/sync` command now carries over notifications when switching to a new Twitter account. 

## 0.3.5 (November 12, 2023)  
**✨Features:**  
- Added the `/list users` slash command for viewing all monitored users. 
- Enhanced reliability to handle multiple tweets posted in quick succession. 

**🐛Fixes:**  
- Fixed “Missing Access” error when sending messages to channels. 
- Ensured automatic creation of the data directory if it does not exist. 
- Corrected errors when the data directory exists but the database file is located elsewhere. 

**🎉New Contributors:**
- @me846 made their first contribution in [#17](https://github.com/Yuuzi261/Tweetcord/pull/17) 

## 0.3.4 (October 23, 2023)  
**✨Features:**  
- Introduced the `remove notifier` slash command for easy notifier removal. 
- Added a command for owners to download log files. 

**🐛Fixes:**
- Resolved errors when the specified channel could not be found. 
- Addressed database locking conflicts during concurrent task updates. 

## 0.3.3 (October 7, 2023)  
**♻️Refactor:**  
- Migrated data storage from JSON files to an SQLite database for improved stability and performance.
