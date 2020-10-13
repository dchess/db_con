FROM python:3.8
WORKDIR /code
# SQL dependencies
RUN mkdir -p /opt/oracle
RUN wget https://packages.microsoft.com/debian/9/prod/pool/main/m/msodbcsql17/msodbcsql17_17.5.2.1-1_amd64.deb
RUN wget https://download.oracle.com/otn_software/linux/instantclient/193000/instantclient-basic-linux.x64-19.3.0.0.0dbru.zip -P /opt/oracle
RUN cd /opt/oracle && unzip instantclient-basic-linux.x64-19.3.0.0.0dbru.zip
RUN ln -s /opt/oracle/instantclient_19_3/libclntsh.so.19.1 /opt/oracle/libclntsh.so
ENV LD_LIBRARY_PATH="/opt/oracle/instantclient_19_3:${LD_LIBRARY_PATH}"
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y unixodbc unixodbc-dev
RUN apt-get install -y libaio1
RUN yes | dpkg -i msodbcsql17_17.5.2.1-1_amd64.deb
# Python dependencies
RUN pip install pipenv
COPY Pipfile .
RUN pipenv install --skip-lock
COPY ./ .
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait
