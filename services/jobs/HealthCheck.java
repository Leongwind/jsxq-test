import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
public class HealthCheck {
  public static void main(String[] args) throws Exception {
    var request=HttpRequest.newBuilder(URI.create("http://127.0.0.1:8081/actuator/health")).timeout(Duration.ofSeconds(3)).build();
    var response=HttpClient.newHttpClient().send(request,HttpResponse.BodyHandlers.discarding());
    if(response.statusCode()!=200) System.exit(1);
  }
}
