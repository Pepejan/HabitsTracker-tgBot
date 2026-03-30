"""locales/en.py — English strings"""

STRINGS = {
    # /start
    "start_greeting":        "👋 Hi, <b>{name}</b>!\n\n📅 <b>{date}</b>\n📊 Progress: <b>{bar}</b>  {done}/{total}\n\nTap a habit to mark it done 👇",

    # /stats
    "stats_empty":           "📭 <b>No stats yet!</b>\n\nStart by marking some habits with /start",
    "stats_header":          "📋 <b>Recent Activity</b>\n\n",

    # /week
    "week_empty":            "📭 <b>No data for this week yet!</b>\n\nStart tracking habits with /start",
    "week_header":           "📊 <b>Weekly Summary</b>\n━━━━━━━━━━━━━━━━\n\n",
    "week_today":            " ← today",
    "week_best":             " 🏆",
    "week_footer_total":     "🔢 Total this week: <b>{total}</b> habits\n",
    "week_footer_active":    "📅 Active days: <b>{active}/7</b>\n",
    "week_footer_avg":       "📈 Daily average: <b>{avg}</b>\n",
    "week_perfect":          "\n🔥 <b>Perfect week! Keep it up!</b>",
    "week_great":            "\n💪 <b>Great consistency!</b>",
    "week_good":             "\n👍 <b>Good progress, push for more!</b>",
    "week_starting":         "\n🌱 <b>Just getting started — you got this!</b>",

    # /add
    "add_usage":             "➕ <b>Add a new habit</b>\n\nUsage:\n<code>/add Reading</code>\n<code>/add Meditate</code>\n<code>/add No sugar</code>",
    "add_duplicate":         "🙈 Oh, you already have <b>{habit}</b> in your habits!\n\nUse /myhabits to see your full list.",
    "add_pick_emoji":        "✏️ New habit: <b>{habit}</b>\n\nPick an emoji for it 👇",
    "add_already_exists":    "🙈 Looks like <b>{habit}</b> already exists in your habits!\n\nUse /myhabits to see your full list.",
    "add_success":           "{emoji} <b>'{habit}'</b> added to your habits!\n\nUse /start to see your updated list.",
    "add_callback_answer":   "Habit added! 🎉",

    # /myhabits
    "myhabits_empty":        "📭 You have no custom habits yet.\n\nUse /add to create one!",
    "myhabits_header":       "📋 <b>Your Habits</b>\n\n",
    "myhabits_total":        "\n\n<i>Total: {count} habits</i>",

    # default habits (display names shown in UI; stored internally as canonical English keys)
    "default_habits": ["Water", "Exercise", "Read"],

    # /remove
    "remove_nothing":          "📭 <b>Nothing to remove.</b>\n\nYou have no habits yet. Use /add to create one!",
    "remove_empty":            "📭 <b>No custom habits to delete.</b>\n\nDefault habits (Water, Exercise, Read) cannot be removed.\nUse /add to create your own habits.",
    "remove_header":           "🗑️ <b>Delete a habit</b>\n\nChoose which habit to remove.\n<i>Default habits (🔒) will be hidden but can be re-enabled with /restore.</i>",
    "remove_ask":              "🗑️ Delete <b>{habit}</b>?\n\n{note}",
    "remove_ask_default_note": "<i>This is a built-in habit. It will be hidden from your list.\nPast completions won't be affected. Use /restore to bring it back.</i>",
    "remove_ask_custom_note":  "<i>This will permanently remove it from your habit list.\nPast completions won't be affected.</i>",
    "remove_confirm_answer":   "🗑️ '{habit}' removed!",
    "remove_done_more":        "✅ <b>{habit}</b> removed.\n\n🗑️ <b>Remove another?</b>",
    "remove_done_empty":       "✅ <b>{habit}</b> removed.\n\n📭 No more habits to remove.",
    "remove_back_header":      "🗑️ <b>Delete a habit</b>\n\nChoose which habit to remove.",
    "remove_cancelled":        "↩️ Cancelled. Your habits are safe!",
    "btn_built_in_badge":      "🔒",

    # habit callbacks
    "habit_done_text":       "{emoji} <b>{habit}</b> — done!\n\n📊 Progress: <b>{bar}</b>  {done}/{total}\n✅ Done today: {done_list}",
    "habit_already_done":    "⚠️ Already done today!",
    "habit_marked":          "✅ Marked!",

    # keyboard buttons
    "btn_yes_delete":        "✅ Yes, delete",
    "btn_go_back":           "↩️ Go back",
    "btn_cancel":            "✖️ Cancel",
    "btn_auto_detect":       "✨ Auto-detect  ({emoji} {habit})",
    "btn_built_in_badge":    "🔒",

    # /restore
    "restore_nothing":   "✅ <b>All default habits are active.</b>\n\nYou haven't hidden any built-in habits.",
    "restore_header":    "♻️ <b>Restore a habit</b>\n\nThese default habits are currently hidden. Tap one to bring it back.",
    "restore_answer":    "♻️ '{habit}' restored!",
    "restore_done_more": "✅ <b>{habit}</b> restored!\n\n♻️ <b>Restore another?</b>",
    "restore_done_all":  "✅ <b>{habit}</b> restored!\n\n🎉 All default habits are active again.",

    # /help
    "help_text": (
        "📘 <b>Help</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🗂 <b>Commands</b>\n\n"
        "/start — Open habit tracker & mark habits\n"
        "/stats — View recent activity (last 7 days)\n"
        "/week — 📊 Weekly chart summary\n"
        "/add &lt;habit&gt; — Create a custom habit\n"
        "/myhabits — List all your habits\n"
        "/remove — 🗑️ Remove a habit\n"
        "/restore — ♻️ Restore a hidden default habit\n"
        "/language — 🌐 Change language\n"
        "/help — Show this guide\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "💡 <b>Tips</b>\n\n"
        "• Tap any habit in /start to mark it ✅\n"
        "• You can add unlimited custom habits\n"
        "• Your streak builds when you're consistent\n"
        "• Check /week every Sunday to review progress\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "📦 <b>Examples</b>\n\n"
        "<code>/add Meditation</code>\n"
        "<code>/add No sugar</code>\n"
        "<code>/add Cold shower</code>"
    ),

    # /language
    "language_choose":       "🌐 <b>Choose your language:</b>",
    "language_set":          "✅ Language set to <b>English</b>!",

    # export / import (admin, kept in English)
    "export_empty":          "📭 <b>Nothing to export yet.</b>",
    "export_caption":        "📦 <b>Habit data export</b>\n\n✅ Custom habits: <b>{habits}</b>\n📅 Completion records: <b>{completions}</b>",
    "export_failed":         "❌ Export failed: <code>{error}</code>",
    "import_prompt":         "📂 <b>Send your export JSON file now.</b>\n\n<i>Only habits_export_*.json files are accepted.</i>",
    "import_bad_ext":        "❌ Please send a valid <code>.json</code> export file.",
    "import_bad_format":     "❌ Invalid export file format.",
    "import_success":        "✅ <b>Import complete!</b>\n\n➕ Habits imported: <b>{habits_added}</b>\n⏭ Habits skipped (already exist): <b>{habits_skipped}</b>\n📅 Completions imported: <b>{completions_added}</b>\n⏭ Completions skipped (duplicates): <b>{completions_skipped}</b>",
    "import_bad_json":       "❌ Could not parse the file. Is it a valid JSON?",
    "import_failed":         "❌ Import failed: <code>{error}</code>",
    "import_wrong_input":    "❌ Expected a JSON file. Import cancelled.",

    # scheduler reminders
    "reminders": [
        "☀️ <b>Good morning!</b>\n\nYour habits are waiting. Start strong and make today count! 💪",
        "🌅 <b>Rise and shine!</b>\n\nA new day, a new chance to build great habits. Let's go! 🔥",
        "👋 <b>Hey, it's habit time!</b>\n\nSmall actions every day add up to big results. Open /start and let's do this! 🚀",
        "⏰ <b>Daily check-in!</b>\n\nDon't forget your habits today — your future self will thank you. 🌟",
    ],

    # congrats (all habits done)
    "congrats": [
        "🎉 <b>You crushed it today!</b>\n\nEvery single habit — done. That's not luck, that's discipline. Let's make tomorrow just as legendary! 💪",
        "🏆 <b>Perfect day achieved!</b>\n\nYou completed every habit today. Champions are made from days like this. See you tomorrow! 🌅",
        "🌟 <b>100% complete!</b>\n\nLook at you go! All habits done for today. Come back tomorrow and do it all over again! 🔥",
        "✨ <b>Flawless!</b>\n\nNot one habit missed. You're building something real here — keep that streak alive tomorrow! 🚀",
    ],
}