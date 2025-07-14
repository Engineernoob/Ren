// main.js - Electron entry point for Ren's MacBook Nook UI
const { app, BrowserWindow, Tray, screen, nativeImage } = require('electron');
const path = require('path');

let tray = null;
let win = null;

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width } = primaryDisplay.workAreaSize;

  win = new BrowserWindow({
    width: 300,
    height: 70,
    x: Math.round((width - 300) / 2), // center under notch
    y: 10,
    frame: false,
    transparent: true,
    resizable: false,
    show: false,
    alwaysOnTop: true,
    hasShadow: false,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadFile('index.html');
  win.setIgnoreMouseEvents(false);
}

app.whenReady().then(() => {
  createWindow();

  // Optional tray icon if needed later
  tray = new Tray(nativeImage.createEmpty()); // hidden icon
  tray.setToolTip('Ren Assistant');
  tray.on('click', () => {
    win.isVisible() ? win.hide() : win.show();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});