Systemd Deployment
==================

Unit File
---------
Installed at `/etc/systemd/system/seoanalyzepro.service`:
```ini
[Unit]
Description=SEOAnalyzePro - Gunicorn WSGI Server
After=network.target

[Service]
User=shahin
Group=shahin
WorkingDirectory=/home/shahin/seoanalyzepro
Environment="PATH=/home/shahin/seoanalyzepro/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=please-set-strong-secret"
ExecStart=/home/shahin/seoanalyzepro/venv/bin/gunicorn -w 3 -b 127.0.0.1:5000 --timeout 120 app.web.app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Commands
--------
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now seoanalyzepro
sudo systemctl status seoanalyzepro
sudo systemctl restart seoanalyzepro
sudo journalctl -u seoanalyzepro -f
```

Overriding Environment
----------------------
```bash
sudo systemctl edit seoanalyzepro
# Add under [Service]:
# Environment="SECRET_KEY=your-strong-secret"
sudo systemctl daemon-reload && sudo systemctl restart seoanalyzepro
```


