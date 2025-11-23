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
  -e SMTP_USER="<xxx>@gmail.com" \
  -e SMTP_PASS="<xxx>" \
  -e SMTP_HOST="smtp.gmail.com" \
  -e EMAIL_TO="<xxx>@gmail.com" \
  -e SMTP_PORT="587" \
  museum-pass-checker:latest
```
