FROM python:3.7-alpine
WORKDIR /home
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY . .
RUN pip install -r requirement.txt
ENV PYTHONPATH "${PYTHONPATH}:/home"
RUN chmod +x build
CMD ["sh", "build"]

