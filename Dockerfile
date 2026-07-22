FROM python:3.11-slim
RUN apt-get update && apt-get install -y build-essential openssh-server && rm -rf /var/lib/apt/lists/* && echo "root:Docker!" | chpasswd
RUN mkdir -p /run/sshd && echo "Port 2222" >> /etc/ssh/sshd_config && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000 2222

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]