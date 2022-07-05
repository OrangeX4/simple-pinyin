import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import KeyboardIcon from '@mui/icons-material/Keyboard';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Divider, FilledInput, FormControl, Grid, IconButton, InputAdornment, InputLabel, List, ListItem, ListItemButton, ListItemText, Popover, TextField } from '@mui/material';
import Picker from 'emoji-picker-react';

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

// 保存结果
const get_pinyin_cache = {}
function get_pinyin(pinyin, callback) {
  if (get_pinyin_cache[pinyin]) {
    callback(get_pinyin_cache[pinyin])
  }
  fetch(`http://localhost:3366/?pinyin=${pinyin}&limit=7`).then(
    (response) => {
      response.json().then((data) => {
        get_pinyin_cache[pinyin] = data
        callback(data)
      })
    }
  )
}

export default function App() {
  // pinyin
  const [pinyin, setPinyin] = React.useState('');

  // list
  const [list, setList] = React.useState([]);
  const updatePinyin = (value) => {
    if (value) {
      setPinyin(value)
      // GET http://localhost:3366/?pinyin=a&limit=7
      get_pinyin(value, (data) => {
        if (data.status === 'success') {
          setList(data.result)
        }
      })
    } else {
      setPinyin('')
      setList([])
    }
  }
  const handleListClick = (index) => {
    setText(text + list[index].word)
    updatePinyin('')
  }

  // text
  const [text, setText] = React.useState('')
  const handleTextChange = (event) => {
    setText(event.target.value)
  }
  const handleKeydown = (event) => {
    // a-z，拼音输入
    if (event.keyCode >= 65 && event.keyCode <= 90) {
      event.preventDefault()
      updatePinyin(pinyin + event.key)
    }
    // 分词符号 '
    if (event.keyCode === 222) {
      event.preventDefault()
      updatePinyin(pinyin + '\'')
    }
    // backspace，退格
    if (event.keyCode === 8) {
      if (pinyin.length > 0) {
        event.preventDefault()
        updatePinyin(pinyin.substring(0, pinyin.length - 1))
      }
    }
    // 1-9，选择词语
    if (event.keyCode >= 49 && event.keyCode <= 57) {
      if (parseInt(event.key) <= list.length) {
        event.preventDefault()
        setText(text + list[parseInt(event.key) - 1].word)
        updatePinyin('')
      }
    }
    // enter or space，选择第一个词语
    if (event.key === 'Enter' || event.key === ' ') {
      if (list.length) {
        event.preventDefault()
        setText(text + list[0].word)
        updatePinyin('')
      }
    }
  }


  // emoji
  const [anchorEl, setAnchorEl] = React.useState(null)
  const handleEmojiClick = (event) => {
    setAnchorEl(event.currentTarget);
  }
  const handleEmojiClose = () => {
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)
  const id = open ? 'simple-popover' : undefined
  const handleEmojiSelect = (event, emojiObject) => {
    setText(text + emojiObject.emoji)
  }


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="relative">
        <Toolbar>
          <KeyboardIcon sx={{ mr: 2 }} />
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
                <FormControl fullWidth variant="filled">
                  <InputLabel htmlFor="filled-adornment">拼音输入法</InputLabel>
                  <FilledInput
                    id="filled-adornment"
                    value={list.length > 0 ? list[0].pinyin : pinyin}
                    onKeyDown={handleKeydown}
                    endAdornment={
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleEmojiClick}
                          edge="end"
                        >
                          <EmojiEmotionsIcon />
                        </IconButton>
                      </InputAdornment>
                    }
                  />
                </FormControl>
                <Popover
                  id={id}
                  open={open}
                  anchorEl={anchorEl}
                  onClose={handleEmojiClose}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                  }}
                >
                  <Picker onEmojiClick={handleEmojiSelect} />
                </Popover>
                <Box sx={{
                  marginTop: "0.5rem",
                  border: "1px solid #ccc",
                  borderRadius: "0.2rem",
                }}>
                  {pinyin ? (
                    <List>
                      {list.map((item, index) => {
                        return (
                          <>
                            {index ? <Divider /> : null}
                            <ListItem key={index} disablePadding>
                              <ListItemButton onClick={(e) => handleListClick(index)}>
                                <ListItemText primary={(index+1) + ". " + item.word} />
                              </ListItemButton>
                            </ListItem>
                          </>
                        )})}
                    </List>
                  ) : (
                    <Typography sx={{ p: 1 }}>请输入拼音。</Typography>
                  )}
                </Box>
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth multiline rows={17} id="outlined-basic" label="输入文本" variant="outlined"
                value={text} onChange={handleTextChange} onKeyDown={handleKeydown} />
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
