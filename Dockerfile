# Contains the code for packaging up the example module, wrapped in luigi goodness.
# basically pip installing the example package and dependencies
# To Build: docker build . -t <name>:<TAG#>
#
FROM python:3.6.4

# Copy all project files and chdir
COPY . /opt/example
WORKDIR /opt/example

# Volume to save results
VOLUME ["/data"]

# Install requirements
RUN pip install -r requirements.txt

# Install
RUN pip install -e .

EXPOSE 8080
ENTRYPOINT ["example"]
