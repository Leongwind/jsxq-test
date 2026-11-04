package com.careerlens.jobs;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;
import static com.careerlens.jobs.Contracts.*;
@RestControllerAdvice
public class ApiExceptionHandler {
  @ExceptionHandler(ServiceFailure.class) ResponseEntity<ApiError> service(ServiceFailure e,HttpServletRequest request) {
    return ResponseEntity.status(e.status()).body(new ApiError(e.code(),e.getMessage(),(String)request.getAttribute("requestId")));
  }
  @ExceptionHandler({MethodArgumentNotValidException.class,HttpMessageNotReadableException.class}) ResponseEntity<ApiError> invalid(Exception ignored,HttpServletRequest request) {
    return ResponseEntity.badRequest().body(new ApiError("INVALID_INPUT","请检查简历长度，并且只选择预置岗位或输入自定义 JD。",(String)request.getAttribute("requestId")));
  }
  @ExceptionHandler(Exception.class) ResponseEntity<ApiError> unexpected(Exception ignored,HttpServletRequest request) {
    return ResponseEntity.status(503).body(new ApiError("SERVICE_UNAVAILABLE","服务暂时不可用，请稍后重试。",(String)request.getAttribute("requestId")));
  }
}
