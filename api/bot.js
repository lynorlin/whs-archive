// Vercel Serverless Function: Telegram Bot for WHS Archive
// Handles: /notification, /events, /start — NO payment processing (payments go via channel)
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const FUNDER_CHANNEL_ID = "-1004305443024"; // Admin "Funder" Telegram Channel
const BACKUP_CHANNEL_ID = "-1004452088494"; // Secondary Archive Channel
const BASE_URL = "https://whs-archive.vercel.app";
const FUNDER_CHANNEL_INVITE = "https://t.me/+d7riC1CS1eowZGFl";

async function callTg(method, payload) {
  try {
    const r = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return await r.json();
  } catch (err) {
    console.error(`[TG] ${method}:`, err);
    return { ok: false, error: err.message };
  }
}

export default async function handler(req, res) {
  // ── GET helper endpoints ──────────────────────────────────────────────────
  if (req.method === "GET") {
    const action = req.query.action || "info";

    if (action === "setWebhook") {
      const webhookUrl = `${BASE_URL}/api/bot`;
      const result = await callTg("setWebhook", {
        url: webhookUrl,
        allowed_updates: ["message", "edited_message", "channel_post"]
      });
      return res.status(200).json({ ok: true, webhookUrl, result });
    }
    if (action === "webhookInfo") {
      return res.status(200).json(await callTg("getWebhookInfo", {}));
    }
    if (action === "getMe") {
      return res.status(200).json(await callTg("getMe", {}));
    }
    if (action === "testChannel") {
      const r = await callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text: "⚡ Bot connectivity test — Funder admin channel active.",
        parse_mode: "Markdown"
      });
      return res.status(200).json({ ok: true, result: r });
    }

    return res.status(200).json({
      status: "online", bot: "whs1966_bot",
      funderChannel: FUNDER_CHANNEL_ID
    });
  }

  // ── POST: Telegram Webhook ────────────────────────────────────────────────
  if (req.method === "POST") {
    const update = req.body || {};
    const message = update.message || update.edited_message;
    if (!message) return res.status(200).json({ ok: true });

    const chatId    = message.chat.id;
    const isPrivate = message.chat.type === "private";
    const text      = (message.text || "").trim();
    const user      = message.from || {};
    const firstName = user.first_name || "WHS Patron";
    const username  = user.username ? `@${user.username}` : `ID:${user.id}`;
    const lower     = text.toLowerCase();
    const dateStr   = new Date().toISOString().replace("T"," ").slice(0,19);

    // ── /funder or /start funder / /start support ─────────────────────────
    if (lower.startsWith("/funder") || lower === "/start funder" || lower === "/start support") {
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `🏛️ *WOODLAND HOUSE SCHOOL ARCHIVE — FUNDER PROGRAM*\n\n` +
          `Support our community archive by joining the Funder channel below. ` +
          `The channel has the owner's pinned message with full payment details.\n\n` +
          `👉 *Join here:* ${FUNDER_CHANNEL_INVITE}\n\n` +
          `⚠️ *Important Transparency:*\n` +
          `• Contributions *strictly* support website hosting, server fees, and website-team digital events.\n` +
          `• Does *NOT* fund school administrative operations or school-run events.\n` +
          `• Non-profit. 100% free access. No personal data collected.\n\n` +
          `Once your contribution is verified, your name appears on the site:\n` +
          `🔗 ${BASE_URL}/#funders`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "funder_info" });
    }

    // ── /notification or /start subscribe ─────────────────────────────────
    if (lower.startsWith("/notification") || lower === "/start subscribe" || lower.startsWith("/subscribe")) {
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `🔔 *REAL-TIME EVENT NOTIFICATIONS ACTIVATED!*\n\n` +
          `Hello ${firstName}! You're now subscribed to instant notifications for:\n` +
          `✅ Events hosted by Woodland House School\n` +
          `✅ Digital events hosted by the Website Team\n\n` +
          `You'll receive a message here the moment a new event is announced!\n\n` +
          `💡 *Commands:*\n` +
          `• /funder — Join the Funder channel to support the archive\n` +
          `• /events — View upcoming & past events\n\n` +
          `🔗 ${BASE_URL}`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });

      // Notify admin of new subscriber
      callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text: `🔔 *New Notification Subscriber*\n👤 ${firstName} (${username})\n🆔 \`${user.id}\``,
        parse_mode: "Markdown"
      }).catch(() => {});

      return res.status(200).json({ ok: true, action: "subscribed" });
    }

    // ── /events ────────────────────────────────────────────────────────────
    if (lower.startsWith("/events")) {
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `📅 *WHS ARCHIVE — EVENT CHRONICLE*\n\n` +
          `View real-time upcoming events and the full timeline:\n` +
          `🔗 ${BASE_URL}/#events\n\n` +
          `Use /notification to get instant alerts when new events are added!`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "events" });
    }

    // ── /start ─────────────────────────────────────────────────────────────
    if (lower.startsWith("/start")) {
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `👋 *Welcome to the WHS Archive Bot!*\n\n` +
          `The official bot for the Woodland House School Memory Vault.\n\n` +
          `📌 *Available Commands:*\n\n` +
          `🔔 */notification* — Subscribe to real-time event alerts\n\n` +
          `💳 */funder* — Join the Funder channel & support the archive\n\n` +
          `📅 */events* — View upcoming & past events\n\n` +
          `🔗 *Official Archive:* ${BASE_URL}`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "start" });
    }

    // ── Plain text in private chat → forward to admin ──────────────────────
    if (isPrivate && text) {
      callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text:
          `💬 *User Message*\n` +
          `👤 ${firstName} (${username})\n🆔 \`${user.id}\`\n` +
          `📝 "${text}"\n📅 \`${dateStr} UTC\``,
        parse_mode: "Markdown"
      }).catch(() => {});

      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `📨 Message received, ${firstName}!\n\n` +
          `To support the archive, use */funder* to get the Funder channel link.`,
        parse_mode: "Markdown"
      });
      return res.status(200).json({ ok: true, action: "text_forwarded" });
    }

    return res.status(200).json({ ok: true });
  }

  res.setHeader("Allow", ["GET", "POST"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
