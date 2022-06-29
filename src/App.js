import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import CameraIcon from '@mui/icons-material/PhotoCamera';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Divider, Grid, List, ListItem, ListItemButton, ListItemText, TextField } from '@mui/material';

function Copyright() {
  return (
    <Typography variant="body2" color="text.secondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://orangex4.cool/">
        OrangeX4
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const theme = createTheme();

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="relative">
        <Toolbar>
          <CameraIcon sx={{ mr: 2 }} />
          <Typography variant="h6" color="inherit" noWrap>
            简易智能拼音输入法
          </Typography>
        </Toolbar>
      </AppBar>
      <Container>
      <main>
        {/* Hero unit */}
        <Box
          sx={{
            bgcolor: 'background.paper',
            width: "100%",
            pt: 6,
            pb: 6,
          }}
          >
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField fullWidth id="outlined-basic" label="拼音输入法" value={"pin'yin"} variant="filled" />
                <Box sx={{
                  marginTop: "0.5rem",
                  border: "1px solid #ccc",
                  borderRadius: "0.2rem",
                }}>
                  <List>
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="1. 你好" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="2. 你号" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="3. 拟好" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="4. 拟好" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="5. 拟好" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="6. 拟好" />
                      </ListItemButton>
                    </ListItem>
                    <Divider />
                    <ListItem disablePadding>
                      <ListItemButton>
                        <ListItemText primary="7. 拟好" />
                      </ListItemButton>
                    </ListItem>
                  </List>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth multiline rows={17} id="outlined-basic" label="输入文本" variant="outlined" />
              </Grid>
            </Grid>
        </Box>
      </main>
      </Container>
      
      {/* Footer */}
      <Box sx={{ bgcolor: 'background.paper', p: 6 }} component="footer">
        <Typography
          variant="subtitle1"
          align="center"
          color="text.secondary"
          component="p"
        >
          简易智能输入法
        </Typography>
        <Copyright />
      </Box>
      {/* End footer */}
    </ThemeProvider>
  );
}
