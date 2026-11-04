package com.careerlens.jobs;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import java.io.IOException;
import java.util.List;
import static com.careerlens.jobs.Contracts.*;
@Component
public class JobCatalog {
  private final List<Job> jobs;
  public JobCatalog(ObjectMapper mapper) throws IOException {
    try (var stream = new ClassPathResource("jobs.json").getInputStream()) {
      jobs = List.copyOf(mapper.readValue(stream, new TypeReference<List<Job>>() {}));
    }
  }
  public List<Job> all() { return jobs; }
  public Job get(String id) {
    return jobs.stream().filter(job -> job.id().equals(id)).findFirst()
        .orElseThrow(() -> new ServiceFailure(404,"JOB_NOT_FOUND","岗位不存在，请重新选择。"));
  }
}
