FROM python:3.7

# Setup paths:
ENV DIRPATH /parts_genie_client
WORKDIR $DIRPATH
COPY . .
ENV PYTHONPATH="$DIRPATH:$PYTHONPATH"

# Install Python dependencies:
RUN pip install --upgrade pip \
  && pip install -r requirements.txt
  
# Set ENTRYPOINT:
ENTRYPOINT ["python", "-u", "parts_genie/client.py"]