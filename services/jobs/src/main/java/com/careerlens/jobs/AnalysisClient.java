package com.careerlens.jobs;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Validator;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.*;
import java.net.http.HttpTimeoutException;
import java.net.SocketTimeoutException;
import java.util.Set;
import static com.careerlens.jobs.Contracts.*;
@Component
public class AnalysisClient {
  private static final Set<String> CODES=Set.of("INVALID_INPUT","UNANALYZABLE_JD","RATE_LIMITED","LLM_INVALID_RESPONSE","LLM_UPSTREAM_ERROR","LLM_NOT_CONFIGURED","SERVICE_UNAVAILABLE","UPSTREAM_TIMEOUT");
  private static final Set<Integer> STATUSES=Set.of(400,422,429,502,503,504);
  private final RestClient client;
  private final ObjectMapper mapper;
  private final Validator validator;
  public AnalysisClient(RestClient client, ObjectMapper mapper, Validator validator) { this.client=client;this.mapper=mapper;this.validator=validator; }
  public AnalysisResponse analyze(AnalyzerRequest request,String requestId) {
    try {
      var result=client.post().uri("/internal/analyze").contentType(MediaType.APPLICATION_JSON)
          .header("X-Request-Id",requestId).body(request).retrieve().body(AnalysisResponse.class);
      if(result==null || !validator.validate(result).isEmpty() || !requestId.equals(result.requestId()))
        throw new ServiceFailure(502,"UPSTREAM_ERROR","分析服务返回格式异常，请重试。");
      return result;
    } catch(RestClientResponseException e) {
      try {
        var error=mapper.readValue(e.getResponseBodyAsString(),ApiError.class);
        if(error.code()!=null && CODES.contains(error.code()) && STATUSES.contains(e.getStatusCode().value()))
          throw new ServiceFailure(e.getStatusCode().value(),error.code(),error.message());
      } catch(ServiceFailure known) { throw known; } catch(Exception ignored) { /* Deliberately discard upstream content. */ }
      throw new ServiceFailure(502,"UPSTREAM_ERROR","分析服务暂时不可用，请稍后重试。");
    } catch(ResourceAccessException e) {
      Throwable cause=e;
      while(cause!=null) {
        if(cause instanceof HttpTimeoutException || cause instanceof SocketTimeoutException)
          throw new ServiceFailure(504,"UPSTREAM_TIMEOUT","分析超时，请稍后重试或缩短文本。");
        cause=cause.getCause();
      }
      throw new ServiceFailure(503,"SERVICE_UNAVAILABLE","暂时无法连接分析服务。");
    } catch(RestClientException e) { throw new ServiceFailure(502,"UPSTREAM_ERROR","分析服务返回格式异常，请重试。"); }
  }
}
