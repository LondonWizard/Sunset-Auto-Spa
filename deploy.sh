#!/bin/bash

# Deployment script for Sunset Auto Spa website on AWS EC2

echo "Starting deployment of Sunset Auto Spa website..."

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and pip if not already installed
sudo apt install -y python3 python3-pip python3-venv

# Install nginx
sudo apt install -y nginx

# Create application directory
sudo mkdir -p /var/www/sunset-auto-spa
sudo chown -R $USER:$USER /var/www/sunset-auto-spa

# Copy application files (assumes files are uploaded to home directory)
cp -r ~/sunset-auto-spa/* /var/www/sunset-auto-spa/
cd /var/www/sunset-auto-spa

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create systemd service file
sudo tee /etc/systemd/system/sunset-auto-spa.service > /dev/null <<EOF
[Unit]
Description=Sunset Auto Spa Flask Application
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/sunset-auto-spa
Environment="PATH=/var/www/sunset-auto-spa/venv/bin"
ExecStart=/var/www/sunset-auto-spa/venv/bin/gunicorn --workers 3 --bind unix:sunset-auto-spa.sock -m 007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
sudo tee /etc/nginx/sites-available/sunset-auto-spa > /dev/null <<EOF
server {
    listen 80;
    server_name 3.131.196.78;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/sunset-auto-spa/sunset-auto-spa.sock;
    }

    location /static {
        alias /var/www/sunset-auto-spa/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/sunset-auto-spa /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start and enable services
sudo systemctl daemon-reload
sudo systemctl start sunset-auto-spa
sudo systemctl enable sunset-auto-spa
sudo systemctl restart nginx
sudo systemctl enable nginx

# Configure firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh

echo "Deployment completed!"
echo "Website should be accessible at http://3.131.196.78"
echo ""
echo "To check service status:"
echo "sudo systemctl status sunset-auto-spa"
echo "sudo systemctl status nginx"
echo ""
echo "To view logs:"
echo "sudo journalctl -u sunset-auto-spa -f" 