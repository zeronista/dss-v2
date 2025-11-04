package com.group5.dss.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Customer Data Transfer Object
 * Aggregated customer information from transactions
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CustomerDTO {
    
    private Integer customerId;
    private String country;
    
    // Order Statistics
    private Long totalOrders;
    private Long totalItems;
    private Double totalRevenue;
    private Double averageOrderValue;
    
    // Product Information
    private Long uniqueProductsPurchased;
    
    // Date Information
    private String firstPurchaseDate;
    private String lastPurchaseDate;
    
    // Customer Segment (calculated)
    private String customerSegment; // VIP, Regular, New, At-Risk, etc.
    
    // Risk Information (for Inventory Manager)
    private Long returnedOrders;
    private Double returnRate;
    
    // Activity Status
    private String status; // Active, Inactive, Churned
    private Integer daysSinceLastPurchase;
    
    // Top purchased product
    private String topProductStockCode;
    private String topProductDescription;
    private Long topProductQuantity;
}
