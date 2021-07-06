FROM python:3.9.6-slim-buster

ENV PATH=/home/iaengine/.local/bin:${PATH}
ENV APP_HOME=/app
ENV CELERY_RUN=/var/run/celery/
ENV CELERY_LOG=/var/log/celery/
ENV WEB_LOG=/var/log/ia_engine/
ENV RUN_COLLECT_STATIC=false
ENV RUN_INSTALL_DEPENDENCIES=false
ENV ACCEPT_EULA=Y



WORKDIR /usr/lib/
WORKDIR ${CELERY_RUN}
WORKDIR ${CELERY_LOG}
WORKDIR ${WEB_LOG}
WORKDIR ${APP_HOME}

RUN adduser --disabled-password --gecos '' iaengine

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get install libaio1 -y \
&& apt-get install unzip -y \
&& apt-get install procps -y \
&& apt-get install -y unixodbc-dev \
&& apt-get install -y python3-pip \
&& apt-get install -y curl \
&& apt-get clean

RUN echo "Chegou aqui" 

#RUN dpkg --configure -a
COPY mssql-driver/msodbcsql17_17.7.2.1-1_amd64.deb .
RUN apt install ./msodbcsql17_17.7.2.1-1_amd64.deb -y

COPY --chown=iaengine:iaengine requirements.txt ${APP_HOME} 
COPY --chown=iaengine:iaengine entrypoint.sh /opt

RUN chown -R iaengine:iaengine ${APP_HOME} ${CELERY_RUN} ${CELERY_LOG} \
        ${WEB_LOG} && \
        chmod u+x /opt/entrypoint.sh ${CELERY_RUN} ${CELERY_LOG} && \
        chmod -R g+rwx,o+rwx ${APP_HOME}

EXPOSE 8000

#RUN chmod +x /app/entrypoint.sh ${CELERY_RUN} ${CELERY_LOG}
USER iaengine

RUN pip install --upgrade pip \
    && pip install -r requirements.txt
#CMD tail -f /dev/null
RUN ls -l
CMD ["/opt/entrypoint.sh"]