Operations and Troubleshooting
==============================

Check Service Health
--------------------
- App health: `curl http://127.0.0.1:5000/health`
- Systemd status: `sudo systemctl status seoanalyzepro`
- Logs (follow): `sudo journalctl -u seoanalyzepro -f`

Common Issues
-------------
1) Cannot log in
   - Ensure default admin exists: `python -c "from app.services.storage import UserStorage; UserStorage().ensure_default_admin()"`
   - Check `app/users.json` exists and readable by the service user.

2) Changes not reflected
   - Restart service: `sudo systemctl restart seoanalyzepro`
   - Check Gunicorn workers successfully reloaded.

3) Nginx shows 502/504
   - App down? Check `systemctl status seoanalyzepro` and logs.
   - Upstream timeout? Increase `proxy_read_timeout` in Nginx if analyses become long-running.

4) Permission errors writing results
   - Ensure directories exist and are writable by service user.

5) SECRET_KEY warnings
   - Set a strong key in the systemd unit environment and restart.

Nginx Commands
--------------
```bash
sudo nginx -t
sudo systemctl reload nginx
sudo tail -n 200 -f /var/log/nginx/seoanalyzepro.error.log
```


