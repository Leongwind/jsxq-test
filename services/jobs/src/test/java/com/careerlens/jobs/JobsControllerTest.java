package com.careerlens.jobs;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static com.careerlens.jobs.Contracts.*;
@WebMvcTest(JobsController.class)
@Import(JobCatalog.class)
class JobsControllerTest {
  @Autowired MockMvc mvc;
  @MockitoBean AnalysisClient client;
  @Test void listsSourcedJobs() throws Exception {
    mvc.perform(get("/internal/jobs")).andExpect(status().isOk())
      .andExpect(jsonPath("$.jobs.length()").value(2)).andExpect(jsonPath("$.jobs[0].sourceUrl").isNotEmpty());
  }
  @Test void missingJobIs404() throws Exception {
    mvc.perform(get("/internal/jobs/no-such-job")).andExpect(status().isNotFound()).andExpect(jsonPath("$.code").value("JOB_NOT_FOUND"));
  }
  @Test void rejectsAmbiguousAndBlankInputs() throws Exception {
    for(String input : new String[]{"{}","{\"resumeText\":\" \",\"jobId\":\"java-campus\"}",
      "{\"resumeText\":\"Java\",\"jobId\":\"java-campus\",\"jobText\":\"Java\"}",
      "{\"resumeText\":\"Java\",\"jobText\":\" \"}",
      "{\"resumeText\":\"Java\",\"jobId\":\"java-campus\",\"unknown\":true}"}) {
      mvc.perform(post("/internal/analyses").contentType("application/json").content(input))
        .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("INVALID_INPUT"));
    }
    verifyNoInteractions(client);
  }
  @Test void rejectsLongText() throws Exception {
    mvc.perform(post("/internal/analyses").contentType("application/json")
      .content("{\"resumeText\":\""+"x".repeat(20001)+"\",\"jobId\":\"java-campus\"}")).andExpect(status().isBadRequest());
  }
  @Test void resolvesPresetBeforeCallingAnalyzer() throws Exception {
    when(client.analyze(any(),anyString())).thenReturn(AnalysisClientTest.sample("request-123"));
    mvc.perform(post("/internal/analyses").header("X-Request-Id","request-123").contentType("application/json")
      .content("{\"resumeText\":\"Java project\",\"jobId\":\"java-campus\"}"))
      .andExpect(status().isOk()).andExpect(jsonPath("$.score").value(75));
    verify(client).analyze(argThat(r -> r.job().id().equals("java-campus") && r.job().description().contains("Spring Boot")),eq("request-123"));
  }
  @Test void forwardsCustomText() throws Exception {
    when(client.analyze(any(),anyString())).thenReturn(AnalysisClientTest.sample("request-123"));
    mvc.perform(post("/internal/analyses").header("X-Request-Id","request-123").contentType("application/json")
      .content("{\"resumeText\":\"Java\",\"jobText\":\"Java required\"}")).andExpect(status().isOk());
    verify(client).analyze(argThat(r -> r.job().id().equals("custom") && r.job().description().equals("Java required")),eq("request-123"));
  }
  @Test void mapsTimeout() throws Exception {
    when(client.analyze(any(),anyString())).thenThrow(new ServiceFailure(504,"UPSTREAM_TIMEOUT","分析超时"));
    mvc.perform(post("/internal/analyses").contentType("application/json").content("{\"resumeText\":\"Java\",\"jobText\":\"Java\"}"))
      .andExpect(status().isGatewayTimeout()).andExpect(jsonPath("$.requestId").isNotEmpty());
  }
}
