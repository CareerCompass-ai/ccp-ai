FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./pkg/requirements.txt

# Make port 5010 available to the world outside this container
EXPOSE 5010

# Run app.py when the container launches
CMD ["python", "app.py"]
