package com.group5.dss.controller;

import com.group5.dss.service.ExternalApiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/gateway")
public class ApiGatewayController {
    
    @Autowired
    private ExternalApiService externalApiService;
    
    // ============ INVENTORY APIs ============
    
    @PostMapping("/inventory/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'INVENTORY_MANAGER')")
    public ResponseEntity<Map<String, Object>> callInventoryApi(
            @PathVariable String endpoint,
            @RequestBody(required = false) Map<String, Object> requestBody) {
        Map<String, Object> result = externalApiService.post("inventory", "/" + endpoint, requestBody);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/inventory/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'INVENTORY_MANAGER')")
    public ResponseEntity<Map<String, Object>> getInventoryApi(@PathVariable String endpoint) {
        Map<String, Object> result = externalApiService.get("inventory", "/" + endpoint);
        return ResponseEntity.ok(result);
    }
    
    // ============ MARKETING APIs ============
    
    @PostMapping("/marketing/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MARKETING_MANAGER')")
    public ResponseEntity<Map<String, Object>> callMarketingApi(
            @PathVariable String endpoint,
            @RequestBody(required = false) Map<String, Object> requestBody) {
        Map<String, Object> result = externalApiService.post("marketing", "/" + endpoint, requestBody);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/marketing/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MARKETING_MANAGER')")
    public ResponseEntity<Map<String, Object>> getMarketingApi(@PathVariable String endpoint) {
        Map<String, Object> result = externalApiService.get("marketing", "/" + endpoint);
        return ResponseEntity.ok(result);
    }
    
    // ============ SALES APIs ============
    
    @PostMapping("/sales/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SALES_MANAGER')")
    public ResponseEntity<Map<String, Object>> callSalesApi(
            @PathVariable String endpoint,
            @RequestBody(required = false) Map<String, Object> requestBody) {
        Map<String, Object> result = externalApiService.post("sales", "/" + endpoint, requestBody);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/sales/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'SALES_MANAGER')")
    public ResponseEntity<Map<String, Object>> getSalesApi(@PathVariable String endpoint) {
        Map<String, Object> result = externalApiService.get("sales", "/" + endpoint);
        return ResponseEntity.ok(result);
    }
    
    // ============ ANALYTICS APIs ============
    
    @PostMapping("/analytics/{endpoint}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> callAnalyticsApi(
            @PathVariable String endpoint,
            @RequestBody(required = false) Map<String, Object> requestBody) {
        Map<String, Object> result = externalApiService.post("analytics", "/" + endpoint, requestBody);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/analytics/{endpoint}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Map<String, Object>> getAnalyticsApi(@PathVariable String endpoint) {
        Map<String, Object> result = externalApiService.get("analytics", "/" + endpoint);
        return ResponseEntity.ok(result);
    }
    
    // ============ HEALTH CHECK ============
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, Boolean>> checkAllApis() {
        Map<String, Boolean> statuses = externalApiService.getAllApiStatuses();
        return ResponseEntity.ok(statuses);
    }
}

