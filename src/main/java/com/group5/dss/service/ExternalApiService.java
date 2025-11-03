package com.group5.dss.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class ExternalApiService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Value("${api.inventory.url}")
    private String inventoryApiUrl;
    
    @Value("${api.marketing.url}")
    private String marketingApiUrl;
    
    @Value("${api.sales.url}")
    private String salesApiUrl;
    
    @Value("${api.analytics.url}")
    private String analyticsApiUrl;
    
    /**
     * Generic method to call external API
     * @param apiType: "inventory", "marketing", "sales", "analytics"
     * @param endpoint: API endpoint path (e.g., "/predict")
     * @param method: HTTP method (GET, POST, etc.)
     * @param requestBody: Request body (null for GET)
     * @return API response as Map
     */
    public Map<String, Object> callExternalApi(String apiType, String endpoint, HttpMethod method, Object requestBody) {
        String baseUrl = getBaseUrl(apiType);
        String fullUrl = baseUrl + endpoint;
        
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<?> entity = new HttpEntity<>(requestBody, headers);
            
            @SuppressWarnings("rawtypes")
            ResponseEntity<Map> response = restTemplate.exchange(
                fullUrl,
                method,
                entity,
                Map.class
            );
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response.getBody());
            result.put("statusCode", response.getStatusCode().value());
            
            return result;
            
        } catch (HttpClientErrorException | HttpServerErrorException e) {
            // API returned error (4xx, 5xx)
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", e.getMessage());
            errorResult.put("statusCode", e.getStatusCode().value());
            errorResult.put("apiType", apiType);
            return errorResult;
            
        } catch (ResourceAccessException e) {
            // Connection timeout or API not available
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", "API không khả dụng hoặc timeout: " + apiType);
            errorResult.put("message", e.getMessage());
            errorResult.put("apiType", apiType);
            return errorResult;
            
        } catch (Exception e) {
            // Other errors
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", "Lỗi không xác định khi gọi API: " + apiType);
            errorResult.put("message", e.getMessage());
            errorResult.put("apiType", apiType);
            return errorResult;
        }
    }
    
    /**
     * Shorthand for GET request
     */
    public Map<String, Object> get(String apiType, String endpoint) {
        return callExternalApi(apiType, endpoint, HttpMethod.GET, null);
    }
    
    /**
     * Shorthand for POST request
     */
    public Map<String, Object> post(String apiType, String endpoint, Object requestBody) {
        return callExternalApi(apiType, endpoint, HttpMethod.POST, requestBody);
    }
    
    /**
     * Check if external API is available
     */
    public boolean isApiAvailable(String apiType) {
        String baseUrl = getBaseUrl(apiType);
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(baseUrl + "/health", String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * Get base URL for API type
     */
    private String getBaseUrl(String apiType) {
        switch (apiType.toLowerCase()) {
            case "inventory":
                return inventoryApiUrl;
            case "marketing":
                return marketingApiUrl;
            case "sales":
                return salesApiUrl;
            case "analytics":
                return analyticsApiUrl;
            default:
                throw new IllegalArgumentException("Unknown API type: " + apiType);
        }
    }
    
    /**
     * Get all API statuses
     */
    public Map<String, Boolean> getAllApiStatuses() {
        Map<String, Boolean> statuses = new HashMap<>();
        statuses.put("inventory", isApiAvailable("inventory"));
        statuses.put("marketing", isApiAvailable("marketing"));
        statuses.put("sales", isApiAvailable("sales"));
        statuses.put("analytics", isApiAvailable("analytics"));
        return statuses;
    }
}

