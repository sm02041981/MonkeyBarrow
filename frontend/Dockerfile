# Stage 1: Build the Flutter web app
FROM debian:latest AS build-env

# Install dependencies
RUN apt-get update && apt-get install -y curl git unzip

# Clone the flutter repo
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter

# Set flutter path
ENV PATH="/usr/local/flutter/bin:/usr/local/flutter/bin/cache/dart-sdk/bin:${PATH}"

# Run flutter doctor
RUN flutter doctor

# Enable web
RUN flutter config --enable-web

# Build the app
WORKDIR /app
COPY . .
RUN flutter pub get
RUN flutter build web

# Stage 2: Serve the app with Nginx
FROM nginx:alpine
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Expose port 80 (Cloud Run handles SSL and routes port 8080 to container's port 80 by default or we can map it)
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
