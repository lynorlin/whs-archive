export default async function handler(req, res) {
  const fileId = req.query.id;
  if (!fileId) {
    return res.status(400).send('No file ID provided');
  }

  const botToken = "8781356380:AAGc1w9SBiV6AOMtpNO_JpypaeXdW54WwMw";

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
