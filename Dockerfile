FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY ./dep/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5010 available to the world outside this container
EXPOSE 5010

# Run main.py when the container launches
CMD ["python3", "main.py"]
