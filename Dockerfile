FROM python:3.7-buster

# RUN groupadd -r declis && useradd -r -g declis declis
RUN groupadd -g 1016 declis && useradd -u 1016 -g declis declis

WORKDIR /home/declis

COPY requirements.txt requirements.txt
#RUN python -m venv venv
#RUN venv/bin/pip install gunicorn
#RUN venv/bin/pip install -r requirements.txt
RUN pip3 install --no-cache-dir gunicorn
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app app
# COPY data data
# COPY migrations migrations
# COPY app.db app.db
COPY declis.py config.py ./

ENV FLASK_APP declis.py

RUN chown -R declis:declis ./
USER declis

EXPOSE 5000

# ENTRYPOINT ["./boot.sh"]

ENV GUNICORN_CMD_ARGS "-b :5000 --forwarded-allow-ips='*' --access-logfile - --error-logfile -"

CMD ["gunicorn", "declis:app"]
