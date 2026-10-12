const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const projDir = 'c:/Users/rodri/gitSpace/gTray';
const sessionId = Math.floor(10000 + Math.random() * 90000) + '-' + Math.floor(Date.now() / 1000);
const sessionDir = path.join(projDir, '.superpowers', 'brainstorm', sessionId);

fs.mkdirSync(path.join(sessionDir, 'content'), { recursive: true });
fs.mkdirSync(path.join(sessionDir, 'state'), { recursive: true });

const env = {
  ...process.env,
  BRAINSTORM_DIR: sessionDir,
  BRAINSTORM_HOST: '127.0.0.1',
  BRAINSTORM_URL_HOST: 'localhost',
  BRAINSTORM_OPEN: '1',
  BRAINSTORM_PORT_FILE: path.join(projDir, '.superpowers', 'brainstorm', '.last-port'),
  BRAINSTORM_TOKEN_FILE: path.join(projDir, '.superpowers', 'brainstorm', '.last-token'),
};

const serverScript = 'C:/Users/rodri/.gemini/config/skills/brainstorming/scripts/server.cjs';
const child = spawn(process.execPath, [serverScript], {
  env,
  stdio: 'inherit'
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
