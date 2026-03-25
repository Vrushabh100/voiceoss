import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  AppBar, Toolbar, Typography, Box, Drawer, List,
  ListItem, ListItemButton, ListItemText, Card, CardContent,
  Button, TextField, Chip, CircularProgress, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, Switch, FormControlLabel
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const API = 'http://127.0.0.1:8000';
const DRAWER_WIDTH = 220;

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#7c4dff' },
    background: { default: '#0a0a0a', paper: '#1a1a2e' },
  },
});

// ============================================================
// VOICE ASSISTANT PANEL
// ============================================================
function VoicePanel() {
  const [command, setCommand] = useState('');
  const [status, setStatus] = useState('idle');
  const [lastIntent, setLastIntent] = useState(null);
  const [lastResult, setLastResult] = useState(null);
  const [history, setHistory] = useState([]);

  const sendCommand = async () => {
    if (!command.trim()) return;
    setStatus('processing');
    try {
      const resp = await axios.post(`${API}/voice_command`, { text: command });
      const data = resp.data;
      setLastIntent(data.intent);
      setLastResult(data.result);
      setHistory(h => [{
        text: command,
        intent: data.intent,
        result: data.result,
        time: new Date().toLocaleTimeString()
      }, ...h.slice(0, 19)]);
      setCommand('');
    } catch (e) {
      setLastResult({ success: false, error: e.message });
    }
    setStatus('idle');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, color: '#7c4dff', fontWeight: 'bold' }}>
        🎙️ AI Voice Assistant
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" sx={{ mb: 2, color: '#aaa' }}>
            Type a command and press Enter or click Execute
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="e.g. open chrome, search youtube for lofi music..."
              value={command}
              onChange={e => setCommand(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendCommand()}
              size="small"
            />
            <Button
              variant="contained"
              onClick={sendCommand}
              disabled={status === 'processing'}
              sx={{ minWidth: 120 }}
            >
              {status === 'processing'
                ? <CircularProgress size={20} color="inherit" />
                : 'Execute'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {lastIntent && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle2" sx={{ color: '#aaa', mb: 1 }}>
              Last Result
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
              <Chip label={`Action: ${lastIntent.action}`} color="primary" size="small" />
              <Chip label={`Target: ${lastIntent.target || 'none'}`} size="small" />
              {lastIntent.steps && (
                <Chip label={`${lastIntent.steps.length} steps`} color="secondary" size="small" />
              )}
              <Chip
                label={lastResult?.success ? 'Success' : 'Failed'}
                color={lastResult?.success ? 'success' : 'error'}
                size="small"
              />
            </Box>
            {lastResult?.message && (
              <Typography variant="body2" sx={{ color: '#ccc' }}>
                {lastResult.message}
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent>
          <Typography variant="subtitle2" sx={{ color: '#aaa', mb: 2 }}>
            Command History
          </Typography>
          {history.length === 0 && (
            <Typography variant="body2" sx={{ color: '#666' }}>
              No commands yet. Type something above!
            </Typography>
          )}
          {history.map((h, i) => (
            <Box key={i} sx={{
              p: 1.5, mb: 1, borderRadius: 1,
              bgcolor: '#0d0d1a', border: '1px solid #2a2a4a'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2" sx={{ color: '#fff', fontWeight: 'bold' }}>
                  {h.text}
                </Typography>
                <Typography variant="caption" sx={{ color: '#666' }}>
                  {h.time}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <Chip label={h.intent?.action} size="small" color="primary"
                  sx={{ height: 18, fontSize: 10 }} />
                {h.intent?.target && (
                  <Chip label={h.intent.target.slice(0, 30)} size="small"
                    sx={{ height: 18, fontSize: 10 }} />
                )}
                <Chip
                  label={h.result?.success ? '✓' : '✗'}
                  size="small"
                  color={h.result?.success ? 'success' : 'error'}
                  sx={{ height: 18, fontSize: 10 }}
                />
              </Box>
            </Box>
          ))}
        </CardContent>
      </Card>
    </Box>
  );
}

// ============================================================
// PERMISSION MANAGER PANEL
// ============================================================
function PermissionPanel() {
  const [startupApps, setStartupApps] = useState([]);
  const [processes, setProcesses] = useState([]);
  const [disks, setDisks] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [startupResp, procsResp, diskResp, adminResp] = await Promise.all([
        axios.get(`${API}/permissions/startup`),
        axios.get(`${API}/permissions/processes`),
        axios.get(`${API}/permissions/disk`),
        axios.get(`${API}/permissions/admin`),
      ]);
      setStartupApps(startupResp.data.apps || []);
      setProcesses(procsResp.data.processes || []);
      setDisks(diskResp.data.disks || []);
      setIsAdmin(adminResp.data.is_admin);
    } catch (e) {
      console.error('Failed to load permissions:', e);
    }
    setLoading(false);
  };

  const handleDisableStartup = async (name) => {
    await axios.post(`${API}/permissions/disable_startup`, { name });
    setStartupApps(apps => apps.filter(a => a.name !== name));
  };

  const handleKillProcess = async (pid) => {
    await axios.post(`${API}/permissions/kill`, { pid });
    setProcesses(procs => procs.filter(p => p.pid !== pid));
  };

  const filteredProcs = processes.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
      <CircularProgress />
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ mb: 3, color: '#7c4dff', fontWeight: 'bold' }}>
        🛡️ Permission Manager
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
        <Chip label={isAdmin ? '✓ Admin' : '✗ Not Admin'}
          color={isAdmin ? 'success' : 'warning'} />
        <Chip label={`${startupApps.length} Startup Apps`} color="primary" />
        <Chip label={`${processes.length} Processes`} color="secondary" />
        <Button size="small" variant="outlined" onClick={loadData}>
          Refresh
        </Button>
      </Box>

      {/* Disk Usage */}
      {disks.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
              💾 Disk Usage
            </Typography>
            {disks.map((disk, i) => (
              <Box key={i} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">{disk.drive}</Typography>
                  <Typography variant="body2">
                    {disk.used_gb}GB / {disk.total_gb}GB ({disk.percent_used}%)
                  </Typography>
                </Box>
                <Box sx={{ bgcolor: '#2a2a4a', borderRadius: 1, height: 8, mt: 0.5 }}>
                  <Box sx={{
                    bgcolor: disk.percent_used > 80 ? '#f44336' : '#7c4dff',
                    width: `${disk.percent_used}%`, height: 8, borderRadius: 1
                  }} />
                </Box>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Startup Apps */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
            🚀 Startup Applications
          </Typography>
          {startupApps.length === 0 && (
            <Typography variant="body2" sx={{ color: '#666' }}>
              No startup apps found
            </Typography>
          )}
          {startupApps.map((app, i) => (
            <Box key={i} sx={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', p: 1.5, mb: 1,
              borderRadius: 1, bgcolor: '#0d0d1a',
              border: '1px solid #2a2a4a'
            }}>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {app.name}
                </Typography>
                <Typography variant="caption" sx={{ color: '#666' }}>
                  {app.command.slice(0, 60)}...
                </Typography>
              </Box>
              <Button
                size="small"
                color="error"
                variant="outlined"
                onClick={() => handleDisableStartup(app.name)}
              >
                Disable
              </Button>
            </Box>
          ))}
        </CardContent>
      </Card>

      {/* Running Processes */}
      <Card>
        <CardContent>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
            ⚙️ Running Processes
          </Typography>
          <TextField
            fullWidth size="small" placeholder="Search processes..."
            value={search} onChange={e => setSearch(e.target.value)}
            sx={{ mb: 2 }}
          />
          {filteredProcs.length === 0 && (
            <Typography variant="body2" sx={{ color: '#666' }}>
              No processes found
            </Typography>
          )}
          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Process Name</TableCell>
                  <TableCell>PID</TableCell>
                  <TableCell>Memory</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredProcs.slice(0, 50).map((proc, i) => (
                  <TableRow key={i}>
                    <TableCell>{proc.name}</TableCell>
                    <TableCell>{proc.pid}</TableCell>
                    <TableCell>{proc.memory}</TableCell>
                    <TableCell>
                      <Button
                        size="small" color="error"
                        onClick={() => handleKillProcess(proc.pid)}
                      >
                        Kill
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}

// ============================================================
// MAIN APP
// ============================================================
export default function App() {
  const [page, setPage] = useState('voice');

  const navItems = [
    { id: 'voice', label: '🎙️ Voice Assistant' },
    { id: 'permissions', label: '🛡️ Permissions' },
  ];

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>

        {/* Sidebar */}
        <Drawer variant="permanent" sx={{
          width: DRAWER_WIDTH,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            bgcolor: '#0d0d1a',
            borderRight: '1px solid #2a2a4a'
          }
        }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #2a2a4a' }}>
            <Typography variant="h6" sx={{ color: '#7c4dff', fontWeight: 'bold' }}>
              VoiceOS
            </Typography>
            <Typography variant="caption" sx={{ color: '#666' }}>
              AI Windows Assistant
            </Typography>
          </Box>
          <List>
            {navItems.map(item => (
              <ListItem key={item.id} disablePadding>
                <ListItemButton
                  selected={page === item.id}
                  onClick={() => setPage(item.id)}
                  sx={{
                    '&.Mui-selected': { bgcolor: '#1a1a3a' },
                    '&:hover': { bgcolor: '#1a1a2e' }
                  }}
                >
                  <ListItemText primary={item.label}
                    primaryTypographyProps={{ fontSize: 14 }} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Drawer>

        {/* Main Content */}
        <Box sx={{
          flexGrow: 1,
          ml: `${DRAWER_WIDTH}px`,
          minHeight: '100vh',
          bgcolor: '#0a0a0a'
        }}>
          <AppBar position="static" sx={{
            bgcolor: '#0d0d1a',
            borderBottom: '1px solid #2a2a4a'
          }}>
            <Toolbar>
              <Typography variant="h6" sx={{ color: '#fff' }}>
                {page === 'voice' ? '🎙️ Voice Assistant' : '🛡️ Permission Manager'}
              </Typography>
              <Box sx={{ flexGrow: 1 }} />
              <Chip label="TEXT MODE" color="warning" size="small" />
            </Toolbar>
          </AppBar>

          {page === 'voice' && <VoicePanel />}
          {page === 'permissions' && <PermissionPanel />}
        </Box>

      </Box>
    </ThemeProvider>
  );
}