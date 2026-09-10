export default async function handler(req, res) {
  const botToken = "8781356380:AAGc1w9SBiV6AOMtpNO_JpypaeXdW54WwMw";

  if (req.query.action === 'bot') {
    try {
      const meRes = await fetch("https://api.telegram.org/bot" + botToken + "/getMe");
      const me = await meRes.json();
      const updatesRes = await fetch("https://api.telegram.org/bot" + botToken + "/getUpdates");
      const updates = await updatesRes.json();
      return res.status(200).json({ ok: true, bot: me, updates: updates });
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  if (req.query.action === 'notify' && req.query.chat_id) {
    try {
      const msg = req.query.text || "🔔 Woodland House School: Telegram notification test successful!";
      const sendRes = await fetch("https://api.telegram.org/bot" + botToken + "/sendMessage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: req.query.chat_id, text: msg })
      });
      const result = await sendRes.json();
      return res.status(200).json(result);
    } catch (err) {
      return res.status(500).json({ ok: false, error: err.message });
    }
  }

  const fileId = req.query.id;
  if (!fileId) {
    return res.status(400).send('No file ID provided');
  }

  try {
    const tgRes = await fetch("https://api.telegram.org/bot" + botToken + "/getFile?file_id=" + fileId);
    const data = await tgRes.json();

    if (data.ok && data.result.file_path) {
      const fileUrl = "https://api.telegram.org/file/bot" + botToken + "/" + data.result.file_path;
      const fileRes = await fetch(fileUrl);
      if (!fileRes.ok) {
        return res.status(fileRes.status).send('Failed to fetch from Telegram');
      }

      const contentType = fileRes.headers.get('content-type') || (data.result.file_path.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg');
      res.setHeader('Content-Type', contentType);
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');

      const arrayBuffer = await fileRes.arrayBuffer();
      return res.send(Buffer.from(arrayBuffer));
    } else {
      res.status(404).send('File not found in Telegram');
    }
  } catch (error) {
    res.status(500).send('Server error');
  }
}
