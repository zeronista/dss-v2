package com.group5.dss.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Order Data Transfer Object
 * Represents aggregated invoice data by InvoiceNo
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderDTO {
    
    // Order Identification
    private Long invoiceNo;
    private String invoiceDate;
    private Integer invoiceYear;
    private Integer invoiceMonth;
    
    // Customer Information
    private Integer customerId;
    private String country;
    
    // Order Statistics
    private Integer totalItems;        // Total quantity of all items
    private Integer uniqueProducts;    // Number of different products
    private Double totalAmount;        // Total order value
    
    // Order Status
    private String status;             // Completed, Cancelled, etc.
    private Boolean isCancelled;       // True if any item has negative quantity
    
    // Order Items
    private List<OrderItemDTO> items;  // List of items in this order
    
    // Additional Information
    private String dayOfWeek;          // Day of the week order was placed
    private String timeOfDay;          // Morning, Afternoon, Evening
    
    /**
     * Nested class for Order Items
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OrderItemDTO {
        private String stockCode;
        private String description;
        private Integer quantity;
        private Double unitPrice;
        private Double totalPrice;
        private Boolean isCancelled;   // True if quantity is negative
    }
}
