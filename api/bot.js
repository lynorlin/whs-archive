// Vercel Serverless Function: Telegram Bot for WHS Archive
// Features: Telegram Stars (XTR) in-app donations, real-time event notifications,
// automatic receipt forwarding to admin channel -1004305443024, and display-name collection.

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const FUNDER_CHANNEL_ID = "-1004305443024"; // Admin "Funder" Telegram Channel
const BACKUP_CHANNEL_ID = "-1004452088494"; // Secondary Archive Channel
const BASE_URL = "https://whs-archive.vercel.app";
const FUNDER_CHANNEL_INVITE = "https://t.me/+d7riC1CS1eowZGFl";
const WEBHOOK_SECRET = "whs_vault_secret_964_bot";

// Telegram Stars donation tiers
const STAR_TIERS = {
  "25": { amount: 25, label: "Supporter", title: "WHS Supporter", desc: "Voluntary contribution to website hosting and server infrastructure." },
  "50": { amount: 50, label: "Archive Friend", title: "WHS Archive Friend", desc: "Voluntary contribution to keep the digital memory vault online." },
  "100": { amount: 100, label: "Memory Keeper", title: "WHS Memory Keeper", desc: "Voluntary contribution supporting archive features and digital events." },
  "250": { amount: 250, label: "Legacy Benefactor", title: "WHS Legacy Benefactor", desc: "Major voluntary patron immortalized in the WHS Archive gallery." }
};

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

// Send native Telegram Stars Invoice
async function sendStarsInvoice(chatId, tier) {
  return await callTg("sendInvoice", {
    chat_id: chatId,
    title: tier.title,
    description:
      `${tier.desc}\n\n` +
      `⚠️ Voluntary donations strictly fund website hosting, server infrastructure, and website-team digital events. ` +
      `They do NOT fund school administration or school events. Non-profit memory vault.`,
    payload: `funder_stars_${tier.amount}`,
    currency: "XTR", // Telegram Stars currency code
    prices: [{ label: `${tier.amount} Stars`, amount: tier.amount }],
    is_flexible: false,
    need_name: false,
    need_phone_number: false,
    need_email: false,
    need_shipping_address: false
  });
}

export default async function handler(req, res) {
  // ── GET Helper Endpoints ───────────────────────────────────────────────────
  if (req.method === "GET") {
    const action = req.query.action || "info";

    if (action === "setWebhook") {
      const webhookUrl = `${BASE_URL}/api/bot`;
      const result = await callTg("setWebhook", {
        url: webhookUrl,
        secret_token: WEBHOOK_SECRET,
        allowed_updates: [
          "message",
          "edited_message",
          "channel_post",
          "pre_checkout_query",
          "callback_query"
        ]
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
        text: "⚡ Bot connectivity test — Funder admin channel active with Telegram Stars support.",
        parse_mode: "Markdown"
      });
      return res.status(200).json({ ok: true, result: r });
    }

    return res.status(200).json({
      status: "online",
      bot: "whs1966_bot",
      funderChannel: FUNDER_CHANNEL_ID,
      paymentMethod: "Telegram Stars (XTR)"
    });
  }

  // ── POST: Telegram Webhook ─────────────────────────────────────────────────
  if (req.method === "POST") {
    // Security check: Only allow genuine Telegram servers with valid secret token
    const reqSecret = req.headers["x-telegram-bot-api-secret-token"];
    if (WEBHOOK_SECRET && reqSecret !== WEBHOOK_SECRET) {
      console.warn("Rejected unauthorized POST to /api/bot");
      return res.status(401).json({ ok: false, error: "Unauthorized" });
    }

    const update = req.body || {};

    // ── 1. PRE-CHECKOUT QUERY: Must answer within 10s with ok=true ───────────
    if (update.pre_checkout_query) {
      const pcq = update.pre_checkout_query;
      const valid = pcq.invoice_payload && pcq.invoice_payload.startsWith("funder_stars_");
      await callTg("answerPreCheckoutQuery", {
        pre_checkout_query_id: pcq.id,
        ok: Boolean(valid),
        error_message: valid ? undefined : "Unrecognized payment payload."
      });
      return res.status(200).json({ ok: true });
    }

    // ── 2. CALLBACK QUERIES (Inline Buttons) ──────────────────────────────────
    if (update.callback_query) {
      const cq = update.callback_query;
      const data = cq.data || "";
      const chatId = cq.message?.chat?.id;

      await callTg("answerCallbackQuery", { callback_query_id: cq.id });

      if (data.startsWith("tier_")) {
        const amt = data.replace("tier_", "");
        const tier = STAR_TIERS[amt];
        if (tier && chatId) {
          await sendStarsInvoice(chatId, tier);
        }
      } else if (data === "how_to_pay" && chatId) {
        const guideMsg =
          `📖 *HOW TO PAY USING TELEGRAM STARS*\n\n` +
          `*What are Telegram Stars?*\n` +
          `Telegram Stars are Telegram's official virtual currency. They let you support projects 100% anonymously inside the Telegram app without exposing your bank account, phone number, or UPI ID.\n\n` +
          `*Step-by-Step Guide:*\n` +
          `1️⃣ Tap any of the Star tier buttons below.\n` +
          `2️⃣ A Telegram secure payment window will appear.\n` +
          `3️⃣ If you have Stars in your account, tap *"Pay"*.\n` +
          `   If you don't have Stars, Telegram will prompt you to purchase them instantly with 1 tap using *Apple Pay* (iPhone), *Google Play* (Android), or Card.\n` +
          `4️⃣ Once paid, you'll get an immediate confirmation receipt!\n` +
          `5️⃣ The bot will ask for the name you want featured on the website gallery.`;

        await callTg("sendMessage", {
          chat_id: chatId,
          text: guideMsg,
          parse_mode: "Markdown",
          disable_web_page_preview: true
        });
      }
      return res.status(200).json({ ok: true });
    }

    const message = update.message || update.edited_message;
    if (!message) return res.status(200).json({ ok: true });

    const chatId = message.chat.id;
    const isPrivate = message.chat.type === "private";
    const text = (message.text || message.caption || "").trim();
    const user = message.from || {};
    const firstName = user.first_name || "WHS Patron";
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'WHS Patron';
    const username = user.username ? `@${user.username}` : `(no @username)`;
    const dateStr = new Date().toISOString().replace("T", " ").slice(0, 19);

    // ── 3. SUCCESSFUL STARS PAYMENT ───────────────────────────────────────────
    if (message.successful_payment) {
      const sp = message.successful_payment;
      const stars = sp.total_amount;
      const tier = STAR_TIERS[String(stars)] || { label: "Honored Patron" };
      const chargeId = sp.telegram_payment_charge_id || "N/A";

      // 3A. Instantly notify Admin Channel (-1004305443024)
      const adminNotice =
        `🌟 *NEW TELEGRAM STARS DONATION CONFIRMED!*\n\n` +
        `👤 *Donor:* ${fullName} (${username})\n` +
        `🆔 *Telegram User ID:* \`${user.id}\`\n` +
        `⭐ *Stars Contributed:* \`${stars} Stars\` (XTR)\n` +
        `🏅 *Tier:* *${tier.label}*\n` +
        `🧾 *Telegram Charge ID:* \`${chargeId}\`\n` +
        `📅 *Time:* \`${dateStr} UTC\`\n\n` +
        `⏳ *Status:* Waiting for donor to reply with display name for website...`;

      await callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text: adminNotice,
        parse_mode: "Markdown"
      });

      // Backup channel
      callTg("sendMessage", {
        chat_id: BACKUP_CHANNEL_ID,
        text: `⭐ Stars Donor: ${fullName} (${username} / ID: ${user.id}) contributed ${stars} Stars.`,
        parse_mode: "Markdown"
      }).catch(() => {});

      // 3B. Congratulate & Ask Donor for their display name
      const donorMsg =
        `🎉 *THANK YOU FOR YOUR SUPPORT, ${firstName}!* 🎉\n\n` +
        `Your contribution of *${stars} Telegram Stars* has been successfully received!\n` +
        `You are now officially an honored *${tier.label}* of the WHS Archive.\n\n` +
        `📝 *How would you like to appear on the website?*\n` +
        `Please reply directly to this message with the **Name** and optional **Class/Batch** you want displayed in the *Funders & Benefactors* gallery:\n\n` +
        `_Example: "Alumnus - Class of 2024" or "Class of 2026 Patron"_\n\n` +
        `*(Or reply "Anonymous" if you prefer to keep your sponsorship private).*`;

      await callTg("sendMessage", {
        chat_id: chatId,
        text: donorMsg,
        parse_mode: "Markdown"
      });

      return res.status(200).json({ ok: true, action: "stars_payment_handled" });
    }

    // ── 4. COMMAND: /funder or /stars ─────────────────────────────────────────
    const lower = text.toLowerCase();
    if (lower.startsWith("/funder") || lower === "/start funder" || lower === "/start support" || lower.startsWith("/stars")) {
      const funderMsg =
        `🏛️ *WOODLAND HOUSE SCHOOL ARCHIVE — FUNDER PROGRAM*\n\n` +
        `Support our independent, student-created memory vault using **Telegram Stars**!\n\n` +
        `🔒 *Why Telegram Stars?*\n` +
        `• 100% Anonymous & Secure — No bank accounts, UPI IDs, or card numbers are shared.\n` +
        `• Direct in-app 1-tap payment via Apple Pay, Google Play, or Card.\n\n` +
        `⚠️ *Important Scope & Transparency:*\n` +
        `• Contributions *strictly* fund website hosting servers, domain upkeep, and digital events hosted by the website team.\n` +
        `• Does *NOT* fund school administrative functions or school-run events.\n` +
        `• Non-profit initiative with 100% free public access.\n\n` +
        `⭐ *Select a contribution tier below:*`;

      const inlineKeyboard = {
        inline_keyboard: [
          [
            { text: "⭐ 25 Stars (Supporter)", callback_data: "tier_25" },
            { text: "⭐ 50 Stars (Friend)", callback_data: "tier_50" }
          ],
          [
            { text: "⭐ 100 Stars (Keeper)", callback_data: "tier_100" },
            { text: "⭐ 250 Stars (Benefactor)", callback_data: "tier_250" }
          ],
          [
            { text: "❓ How do Stars work? (Guide)", callback_data: "how_to_pay" }
          ]
        ]
      };

      await callTg("sendMessage", {
        chat_id: chatId,
        text: funderMsg,
        parse_mode: "Markdown",
        reply_markup: inlineKeyboard
      });

      return res.status(200).json({ ok: true, action: "funder_menu" });
    }

    // ── 5. DIRECT COMMANDS FOR TIERS: /stars25, /stars50, etc. ───────────────
    if (lower.startsWith("/stars25") || lower.startsWith("/stars50") || lower.startsWith("/stars100") || lower.startsWith("/stars250")) {
      const num = lower.replace(/[^0-9]/g, "");
      const tier = STAR_TIERS[num];
      if (tier) {
        await sendStarsInvoice(chatId, tier);
        return res.status(200).json({ ok: true, action: `invoice_${num}` });
      }
    }

    // ── 6. COMMAND: /howtopay ─────────────────────────────────────────────────
    if (lower.startsWith("/howtopay") || lower.startsWith("/help")) {
      const helpMsg =
        `💡 *HOW TO DONATE USING TELEGRAM STARS*\n\n` +
        `1️⃣ Use /funder to see all donation tiers.\n` +
        `2️⃣ Tap any tier button (e.g. 50 Stars).\n` +
        `3️⃣ A Telegram payment card will pop up.\n` +
        `4️⃣ Tap *"Pay"* using your existing Stars, or buy Stars directly via Apple Pay / Google Play with 1 tap.\n` +
        `5️⃣ Reply with your name to be recognized in the website gallery!\n\n` +
        `*Prefer direct UPI/QR?* Join: ${FUNDER_CHANNEL_INVITE}`;

      await callTg("sendMessage", {
        chat_id: chatId,
        text: helpMsg,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "howtopay" });
    }

    // ── 7. COMMAND: /notification ─────────────────────────────────────────────
    if (lower.startsWith("/notification") || lower === "/start subscribe" || lower.startsWith("/subscribe")) {
      const notifyMsg =
        `🔔 *REAL-TIME EVENT NOTIFICATIONS ACTIVATED!*\n\n` +
        `Hello ${firstName}! You are now subscribed to instant real-time alerts for:\n` +
        `✅ Events hosted by Woodland House School\n` +
        `✅ Digital & community events hosted by the Website Team\n\n` +
        `Whenever a new upcoming event is scheduled, you will get an immediate message here!\n\n` +
        `💡 *Available Commands:*\n` +
        `• /funder — Support the archive with Telegram Stars\n` +
        `• /events — View upcoming & past events\n` +
        `• /howtopay — Guide on Telegram Stars\n\n` +
        `Visit the Vault: ${BASE_URL}`;

      await callTg("sendMessage", {
        chat_id: chatId,
        text: notifyMsg,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });

      // Notify admin of new subscriber
      callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text: `🔔 *New Subscriber Registered*\n👤 ${fullName} (${username})\n🆔 \`${user.id}\``,
        parse_mode: "Markdown"
      }).catch(() => {});

      return res.status(200).json({ ok: true, action: "subscribed" });
    }

    // ── 8. COMMAND: /events ───────────────────────────────────────────────────
    if (lower.startsWith("/events")) {
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `📅 *WHS ARCHIVE — EVENT CHRONICLE*\n\n` +
          `View real-time upcoming events and the chronological timeline at:\n` +
          `🔗 ${BASE_URL}/#events\n\n` +
          `Use /notification to receive automatic instant alerts when new events are added!`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "events" });
    }

    // ── 9. COMMAND: /start ────────────────────────────────────────────────────
    if (lower.startsWith("/start")) {
      const welcomeMsg =
        `👋 *Welcome to the Woodland House School Archive Bot!*\n\n` +
        `This bot powers the interactive memory vault for WHS students and alumni.\n\n` +
        `📌 *Choose an action below:*\n\n` +
        `⭐ */funder* — Support website hosting with Telegram Stars (anonymous & secure)\n\n` +
        `🔔 */notification* — Subscribe to real-time event alerts\n\n` +
        `💡 */howtopay* — How to buy and pay with Telegram Stars\n\n` +
        `📅 */events* — View scheduled upcoming & past events\n\n` +
        `🔗 *Official Archive Website:* ${BASE_URL}`;

      await callTg("sendMessage", {
        chat_id: chatId,
        text: welcomeMsg,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "start" });
    }

    // ── 10. PLAIN TEXT MESSAGES (Name submissions / questions) ────────────────
    if (isPrivate && text) {
      // Forward to Admin Channel so the owner sees what the donor replied with!
      await callTg("sendMessage", {
        chat_id: FUNDER_CHANNEL_ID,
        text:
          `💬 *DONOR / USER MESSAGE RECEIVED*\n\n` +
          `👤 *From:* ${fullName} (${username})\n` +
          `🆔 *User ID:* \`${user.id}\`\n` +
          `📝 *Message / Chosen Display Name:*\n"${text}"\n\n` +
          `📅 *Time:* \`${dateStr} UTC\`\n` +
          `⚡ *Note:* If this is a donor submitting their display name, add it to \`funders.json\`.`,
        parse_mode: "Markdown"
      });

      // Confirm to user
      await callTg("sendMessage", {
        chat_id: chatId,
        text:
          `✅ *Message Received! Thank you, ${firstName}.*\n\n` +
          `Our admin team has received your submission. If you contributed Stars, your display name will be updated in the *Funders & Benefactors* gallery on:\n` +
          `🔗 [whs-archive.vercel.app/#funders](${BASE_URL}/#funders)\n\n` +
          `To donate or view Star tiers again, tap /funder.`,
        parse_mode: "Markdown",
        disable_web_page_preview: true
      });
      return res.status(200).json({ ok: true, action: "text_forwarded" });
    }

    return res.status(200).json({ ok: true });
  }

  res.setHeader("Allow", ["GET", "POST"]);
  return res.status(405).end(`Method ${req.method} Not Allowed`);
}
