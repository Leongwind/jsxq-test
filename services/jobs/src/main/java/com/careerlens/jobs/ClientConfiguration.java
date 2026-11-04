package com.careerlens.jobs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import java.net.http.HttpClient;
import java.time.Duration;
@Configuration
public class ClientConfiguration {
  @Bean RestClient analyzerRestClient(@Value("${analyzer.url}") String url) {
    var client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    var factory=new JdkClientHttpRequestFactory(client);
    factory.setReadTimeout(Duration.ofSeconds(50));
    return RestClient.builder().baseUrl(url).requestFactory(factory).build();
  }
}
