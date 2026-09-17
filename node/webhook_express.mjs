// Receive Unifically task callbacks and verify the signature.
//
//   npm install express
//   UNIFICALLY_WEBHOOK_SECRET=... node webhook_express.mjs
//
// Pass "callback_url" at the top level of POST /v1/tasks. Turn on signing in
// the dashboard under Settings to get the secret.
import crypto from 'node:crypto';
import express from 'express';

const SECRET = process.env.UNIFICALLY_WEBHOOK_SECRET || '';
const TOLERANCE_SECONDS = 300; // replay window, your choice

const app = express();
// Keep the raw bytes. express.json() throws them away after parsing.
app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));

function verified(req) {
  const timestamp = req.headers['x-webhook-timestamp'];
  const signature = req.headers['x-webhook-signature'];
  if (!timestamp || !/^[a-f0-9]{64}$/.test(signature || '')) return false;
  if (Math.abs(Date.now() / 1000 - Number(timestamp)) > TOLERANCE_SECONDS) return false;
  const expected = crypto.createHmac('sha256', SECRET).update(`${timestamp}.${req.rawBody}`).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}

app.post('/webhook', (req, res) => {
  if (SECRET && !verified(req)) return res.sendStatus(401);
  const event = req.body;
  if (event.status === 'completed') console.log('done', event.task_id, event.data);
  else console.log('failed', event.task_id, event.error_message);
  res.sendStatus(200);
});

app.listen(8000, () => console.log('listening on :8000/webhook'));
