package com.careerlens.jobs;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.util.UUID;
@Component
public class RequestIdFilter extends OncePerRequestFilter {
  private static final Logger log=LoggerFactory.getLogger(RequestIdFilter.class);
  @Override protected void doFilterInternal(HttpServletRequest request,HttpServletResponse response,FilterChain chain) throws ServletException,IOException {
    String id=request.getHeader("X-Request-Id");
    if(id==null || !id.matches("[A-Za-z0-9-]{1,64}")) id=UUID.randomUUID().toString();
    request.setAttribute("requestId",id);response.setHeader("X-Request-Id",id);
    long start=System.nanoTime();
    try {chain.doFilter(request,response);} finally {
      log.info("requestId={} method={} status={} durationMs={}",id,request.getMethod(),response.getStatus(),(System.nanoTime()-start)/1_000_000);
    }
  }
}
