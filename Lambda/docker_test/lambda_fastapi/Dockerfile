# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first for better layer caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the main application code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (app.handler refers to the 'handler' object in app.py)
CMD ["app.handler"]