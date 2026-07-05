# ==========================================
# Stage 1 - Build the Spring Boot Application
# ==========================================
FROM maven:3.9.6-eclipse-temurin-17 AS build

WORKDIR /app

# Copy Maven configuration first
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline

# Copy project source
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests


# ==========================================
# Stage 2 - Runtime Image
# ==========================================
FROM eclipse-temurin:17-jre

WORKDIR /app

# Copy generated JAR from build stage
COPY --from=build /app/target/*.jar app.jar

# Expose Spring Boot port
EXPOSE 8080

# JVM options
ENV JAVA_OPTS=""

# Run application
ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar app.jar"]
