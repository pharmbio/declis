FROM python:3.7-buster
# RUN groupadd -r declis && useradd -r -g declis declis
# RUN groupadd -g 1016 declis && useradd -u 1016 -g declis declis
RUN useradd -u 1016 -g www-data declis 

WORKDIR /home/declis
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir gunicorn
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app app
COPY declis.py config.py ./

ENV FLASK_APP declis.py

RUN chown -R declis:www-data ./
USER declis

EXPOSE 5011
ENV GUNICORN_CMD_ARGS "-b :5011 --workers 3 --timeout 120  --forwarded-allow-ips='*' --access-logfile - --error-logfile -"
CMD ["gunicorn", "declis:app"]
