package com.careerlens.jobs;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.List;

public final class Contracts {
  private Contracts() {}
  public record Job(String id, String title, String company, String description, String sourceUrl, String collectedAt) {}
  public record JobsResponse(List<Job> jobs) {}
  public record AnalysisRequest(
      @NotBlank @Size(max=20000) String resumeText,
      @Size(min=1,max=100) @Pattern(regexp="(?s).*\\S.*") String jobId,
      @Size(min=1,max=12000) @Pattern(regexp="(?s).*\\S.*") String jobText) {
    @JsonIgnore @AssertTrue(message="exactly one of jobId/jobText is required")
    public boolean isJobSelectionValid() { return (jobId != null) != (jobText != null); }
  }
  public record AnalysisJob(String id, String title, String description) {}
  public record AnalyzerRequest(String resumeText, AnalysisJob job) {}
  public record JobSummary(@NotBlank String id, @NotBlank String title) {}
  public record Skill(@NotBlank String name, @NotBlank String evidence) {}
  public record Resume(@NotNull String summary, @NotNull List<String> education, @NotNull List<String> experience,
                       @NotNull List<String> projects, @NotNull @Valid List<Skill> skills) {}
  public record Issue(@NotBlank String type, @Pattern(regexp="info|warning") @NotNull String severity,
                      @NotNull String evidence, @NotBlank String suggestion) {}
  public record Match(@NotBlank String name, @Min(1) @Max(3) int weight, @NotBlank String requirementEvidence, @NotBlank String resumeEvidence) {}
  public record Gap(@NotBlank String name, @Min(1) @Max(3) int weight, @NotBlank String requirementEvidence, @NotBlank String suggestion) {}
  public record Breakdown(@Min(0) int matchedWeight, @Min(1) int totalWeight, @NotBlank String formula) {}
  public record Meta(@Pattern(regexp="live|test") @NotNull String mode, @NotBlank String model, @Min(0) long durationMs) {}
  public record AnalysisResponse(@NotBlank String requestId, @NotNull @Valid JobSummary job,
      @NotNull @Valid Resume resume, @NotNull @Valid List<Issue> issues,
      @NotNull @Valid List<Match> matchedSkills, @NotNull @Valid List<Gap> missingSkills,
      @Min(0) @Max(100) int score, @NotNull @Valid Breakdown scoreBreakdown,
      @NotNull List<String> warnings, @NotNull @Valid Meta meta) {}
  public record ApiError(String code, String message, String requestId) {}
}
