// Create a Unifically task, wait for it, print the output URL.
// Node 18+ (built-in fetch). No dependencies.
//
//   export UNIFICALLY_API_KEY=...
//   node generate.mjs video            google/veo-3.1-fast
//   node generate.mjs image            openai/gpt-image-2
//   node generate.mjs music            suno-ai/music
//   node generate.mjs speech           elevenlabs/text-to-speech
//   node generate.mjs video --dry-run  price check only, nothing is charged
//
// Model pages (parameters and a browser playground):
//   https://unifically.com/models/veo-3.1
//   https://unifically.com/models/gpt-image-2
//   https://unifically.com/models/suno
//   https://unifically.com/models/elevenlabs

const API = (process.env.UNIFICALLY_API_BASE_URL || 'https://api.unifically.com').replace(/\/$/, '');
const KEY = process.env.UNIFICALLY_API_KEY;

const EXAMPLES = {
  video: ['google/veo-3.1-fast', { prompt: 'A golden retriever running along a beach at sunset, slow motion, cinematic lighting', duration: 8 }],
  image: ['openai/gpt-image-2', { prompt: 'A cozy wooden cabin in a snowy forest at dusk, warm light in the windows, photorealistic', resolution: '1K' }],
  music: ['suno-ai/music', { mv: 'chirp-hawk', custom: false, gpt_description_prompt: 'An upbeat indie pop song about a summer road trip, bright guitars, catchy chorus' }],
  speech: ['elevenlabs/text-to-speech', { text: 'Welcome to Unifically. This voice was generated with a single API call.' }],
};

async function call(method, path, body) {
  const res = await fetch(API + path, {
    method,
    headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json', 'User-Agent': 'unifically-examples/1.0' },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 500)}`);
  return JSON.parse(text);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  if (!KEY) throw new Error('Set UNIFICALLY_API_KEY first. Keys are at https://unifically.com/api-keys');
  const args = process.argv.slice(2);
  const kind = args.find((a) => !a.startsWith('--')) || 'image';
  if (!EXAMPLES[kind]) throw new Error(`Pick one of: ${Object.keys(EXAMPLES).join(', ')}`);
  const [model, input] = EXAMPLES[kind];

  if (args.includes('--dry-run')) {
    // Validates the request and returns the price. No task is created.
    // The Suno routes do not support dry_run yet.
    const res = await call('POST', '/v1/tasks', { model, input, dry_run: true });
    console.log(`${model} would cost $${res.data.cost}`);
    return;
  }

  const { data: task } = await call('POST', '/v1/tasks', { model, input });
  console.log(`task ${task.task_id} created, status ${task.status}`);

  for (;;) {
    await sleep(5000);
    const { data } = await call('GET', `/v1/tasks/${task.task_id}`);
    if (data.status === 'completed') return console.log(JSON.stringify(data.output, null, 2));
    if (data.status === 'failed') throw new Error(`task failed: ${data.error_message}`);
    console.log('  still', data.status);
  }
}

main().catch((err) => { console.error(err.message); process.exit(1); });
