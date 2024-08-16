# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app/data

# Copy the current directory contents into the container at /app
COPY . /app

# Copy login.py separately to ensure it’s included in the image
COPY login.py /app/data/login.py

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Ensure Python files are executable
RUN chmod +x /app/data/apiload.py
RUN chmod +x /app/data/pgload_competition_3y.py
RUN chmod +x /app/data/pgload_games_3y.py
RUN chmod +x /app/data/pgload_standing_3y.py
RUN chmod +x /app/data/pgload_topscorers_3y.py

# Run apiload.py first, then the other scripts in order
CMD ["bash", "-c", "python apiload.py && python pgload_competition_3y.py && python pgload_games_3y.py && python pgload_standing_3y.py && python pgload_topscorers_3y.py"]
