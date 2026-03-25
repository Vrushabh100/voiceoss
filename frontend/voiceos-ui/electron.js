const { app, BrowserWindow, Tray, Menu } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let pythonProcess;
let tray;

function startPythonBackend() {
    pythonProcess = spawn('cmd.exe', [
        '/c',
        'C:\\VoiceOS\\backend\\venv\\Scripts\\python.exe main.py'
    ], {
        cwd: 'C:\\VoiceOS\\backend',
        shell: false
    });
    pythonProcess.stdout.on('data', d => console.log('[Python]', d.toString()));
    pythonProcess.stderr.on('data', d => console.log('[Python Error]', d.toString()));
    console.log('[Electron] Python backend started');
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: { nodeIntegration: false },
        title: 'VoiceOS',
        icon: path.join(__dirname, 'public', 'favicon.ico'),
        backgroundColor: '#0a0a0a',
    });
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.on('close', (e) => {
        e.preventDefault();
        mainWindow.hide();
    });
}

function createTray() {
    tray = new Tray(path.join(__dirname, 'public', 'favicon.ico'));
    tray.setToolTip('VoiceOS - Running');
    const menu = Menu.buildFromTemplate([
        { label: 'Open VoiceOS', click: () => mainWindow.show() },
        { type: 'separator' },
        { label: 'Quit', click: () => {
            if (pythonProcess) pythonProcess.kill();
            app.exit(0);
        }}
    ]);
    tray.setContextMenu(menu);
    tray.on('click', () => mainWindow.show());
}

app.whenReady().then(() => {
    startPythonBackend();
    setTimeout(() => {
        createWindow();
        createTray();
    }, 4000);
});

app.on('window-all-closed', () => {});