FROM eclipse-temurin:22-jdk

WORKDIR /app

COPY speechassessment ./speechassessment

RUN apt-get update && apt-get install -y maven

WORKDIR /app/speechassessment

RUN mvn clean package -U -DskipTests

EXPOSE 8080

CMD ["java", "-jar", "target/speechassessment-0.0.1-SNAPSHOT.jar"]