ARG MAVEN_IMAGE=maven:3.9.11-eclipse-temurin-21
ARG JAVA_IMAGE=eclipse-temurin:21-jre-jammy
FROM ${MAVEN_IMAGE} AS build
WORKDIR /app
COPY pom.xml ./
COPY src ./src
COPY HealthCheck.java ./
RUN javac HealthCheck.java
RUN mvn -B verify
FROM ${JAVA_IMAGE}
WORKDIR /app
COPY --from=build /app/target/jobs-1.0.0.jar /app/app.jar
COPY --from=build /app/HealthCheck.class /app/HealthCheck.class
USER 10001:10001
EXPOSE 8081
ENTRYPOINT ["java","-XX:MaxRAMPercentage=75","-jar","/app/app.jar"]
