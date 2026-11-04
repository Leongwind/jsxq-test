package com.careerlens.jobs;
import jakarta.validation.Valid;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;
import static com.careerlens.jobs.Contracts.*;
@RestController
@RequestMapping("/internal")
public class JobsController {
  private final JobCatalog catalog;
  private final AnalysisClient analyzer;
  public JobsController(JobCatalog catalog,AnalysisClient analyzer) {this.catalog=catalog;this.analyzer=analyzer;}
  @GetMapping("/jobs") public JobsResponse jobs() {return new JobsResponse(catalog.all());}
  @GetMapping("/jobs/{id}") public Job job(@PathVariable String id) {return catalog.get(id);}
  @PostMapping("/analyses") public AnalysisResponse analyze(@Valid @RequestBody AnalysisRequest input,HttpServletRequest request) {
    AnalysisJob job;
    if(input.jobId()!=null) {var preset=catalog.get(input.jobId());job=new AnalysisJob(preset.id(),preset.title(),preset.description());}
    else job=new AnalysisJob("custom","自定义岗位",input.jobText());
    return analyzer.analyze(new AnalyzerRequest(input.resumeText(),job),(String)request.getAttribute("requestId"));
  }
}
