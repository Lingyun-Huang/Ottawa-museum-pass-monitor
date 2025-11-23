# Ottawa-museum-pass-monitor

## Build image
```
docker build -t museum-pass-checker:latest .
```

## Run image

Sample command
```
docker run  \
  -e TARGET_BRANCHES="Main,Beaverbrook,Vernon" \
  -e GMAIL_USER="<xxx>@gmail.com" \
  -e GMAIL_APP_PASSWORD="<xxx>" \
  -e EMAIL_TO="<xxx>@gmail.com" \
  museum-pass-checker:latest
```

## Sample email

<img width="745" height="221" alt="image" src="https://github.com/user-attachments/assets/c94e1bf8-b27b-41b3-8c73-55ae69daed25" />
