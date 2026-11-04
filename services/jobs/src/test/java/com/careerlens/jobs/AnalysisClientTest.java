package com.careerlens.jobs;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Validation;
import org.junit.jupiter.api.Test;
import org.springframework.http.*;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import java.net.SocketTimeoutException;
import java.util.List;
import static com.careerlens.jobs.Contracts.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;
class AnalysisClientTest {
  static AnalysisResponse sample(String id) {
    return new AnalysisResponse(id,new JobSummary("java-campus","后端开发工程师"),
      new Resume("Java 开发",List.of(),List.of(),List.of(),List.of(new Skill("Java","Java project"))),
      List.of(),List.of(new Match("Java",3,"Java required","Java project")),
      List.of(new Gap("Redis",1,"Redis preferred","简历未体现 Redis 的证据")),
      75,new Breakdown(3,4,"round(100 × matchedWeight / totalWeight)"),List.of(),new Meta("test","test-fixture",1));
  }
  @Test void preservesTypedResponseAndRequestId() throws Exception {
    var builder=RestClient.builder().baseUrl("http://analyzer");
    var server=MockRestServiceServer.bindTo(builder).build();
    var mapper=new ObjectMapper();
    server.expect(requestTo("http://analyzer/internal/analyze")).andExpect(header("X-Request-Id","request-123"))
      .andRespond(withSuccess(mapper.writeValueAsString(sample("request-123")),MediaType.APPLICATION_JSON));
    try(var factory=Validation.buildDefaultValidatorFactory()) {
      var client=new AnalysisClient(builder.build(),mapper,factory.getValidator());
      assertEquals(75,client.analyze(new AnalyzerRequest("Java",new AnalysisJob("custom","自定义","Java")),"request-123").score());
    }
    server.verify();
  }
  @Test void rejectsIncompleteResponse() {
    var builder=RestClient.builder().baseUrl("http://analyzer");
    var server=MockRestServiceServer.bindTo(builder).build();
    server.expect(anything()).andRespond(withSuccess("{\"score\":99}",MediaType.APPLICATION_JSON));
    try(var factory=Validation.buildDefaultValidatorFactory()) {
      var client=new AnalysisClient(builder.build(),new ObjectMapper(),factory.getValidator());
      assertEquals(502,assertThrows(ServiceFailure.class,()->client.analyze(new AnalyzerRequest("Java",new AnalysisJob("x","x","Java")),"id")).status());
    }
  }
  @Test void mapsTransportTimeout() {
    var builder=RestClient.builder().baseUrl("http://analyzer");
    var server=MockRestServiceServer.bindTo(builder).build();
    server.expect(anything()).andRespond(withException(new SocketTimeoutException("sensitive internal address")));
    try(var factory=Validation.buildDefaultValidatorFactory()) {
      var client=new AnalysisClient(builder.build(),new ObjectMapper(),factory.getValidator());
      var error=assertThrows(ServiceFailure.class,()->client.analyze(new AnalyzerRequest("Java",new AnalysisJob("x","x","Java")),"id"));
      assertEquals(504,error.status());assertFalse(error.getMessage().contains("sensitive"));
    }
  }
}
